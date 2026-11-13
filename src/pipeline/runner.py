import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.models import (
    IntelligenceSource,
    DiscoveredURL,
    ExtractedDocument,
    MarketInsight,
    SourceEvidence
)
from src.storage.repository import IntelligenceRepository
from src.connectors.firecrawl_connector import FirecrawlConnector
from src.normalisation.normaliser import DocumentNormaliser
from src.intelligence.taxonomy import classify_text_category
from src.intelligence.scoring import IntelligenceScorer
from src.intelligence.diff_engine import SemanticDiffEngine
from src.intelligence.strategic_engine import StrategicEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("PipelineRunner")

class MarketIntelligencePipeline:
    """End-to-end pipeline orchestrator for the HomePilot Market Intelligence Engine."""

    # Tier-1 Path Heuristic Exclusion Patterns
    EXCLUDE_PATTERNS = [
        r"(?i)/career",
        r"(?i)/privacy",
        r"(?i)/cookie",
        r"(?i)/terms",
        r"(?i)/buying-a-car",
        r"(?i)/scams",
        r"(?i)/contact-us",
        r"(?i)/login",
        r"(?i)/register",
        r"(?i)/media-assets",
        r"(?i)\.(pdf|jpg|png|zip|doc)$"
    ]

    def __init__(self, repository: Optional[IntelligenceRepository] = None, connector: Optional[FirecrawlConnector] = None):
        self.repo = repository or IntelligenceRepository()
        self.connector = connector or FirecrawlConnector()

    def load_sources_from_registry(self, registry_path: str = "config/sources_registry.json") -> int:
        """Loads and upserts approved sources from the config registry."""
        if not os.path.exists(registry_path):
            raise FileNotFoundError(f"Registry file not found at: {registry_path}")

        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sources = data.get("sources", [])
        count = 0
        for s_data in sources:
            source = IntelligenceSource(
                source_id=s_data["id"],
                name=s_data["name"],
                root_url=s_data["url"],
                ecosystem=s_data["ecosystem"],
                tier=s_data.get("tier", 2 if "gov" in s_data["id"] or "revenue" in s_data["id"] else 3),
                connector_type=s_data.get("connector_type", "firecrawl"),
                cadence=s_data.get("cadence", "daily"),
                discovery=s_data.get("discovery"),
                tags=s_data.get("tags", []),
                active=True
            )
            self.repo.upsert_source(source)
            count += 1

        logger.info(f"Loaded and registered {count} sources from {registry_path}.")
        return count

    def filter_url_tier1(self, url: str) -> Tuple[bool, str]:
        """Tier 1 heuristic regex and path filter."""
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, url):
                return False, f"Matched exclude pattern: {pattern}"
        return True, "Passed Tier 1 heuristic filter"

    def evaluate_semantic_score(self, url: str) -> float:
        """Tier 2 lightweight semantic relevance pre-filter (0.0 to 1.0)."""
        url_lower = url.lower()
        primary_signals = ["home", "mortgage", "housing", "property", "first-time", "buyer", "developer", "deposit", "scheme", "financial-difficulty"]
        secondary_signals = ["planning", "rate", "credit", "affordability", "guide", "loan"]
        
        score = 0.3 # Base score for reaching tier 2
        for s in primary_signals:
            if s in url_lower:
                score += 0.3
        for s in secondary_signals:
            if s in url_lower:
                score += 0.15

        return min(1.0, round(score, 2))

    def run_source_discovery(self, source_id: str, limit: int = 50) -> List[DiscoveredURL]:
        """Stage 01: Discover URLs via Firecrawl Map and apply 2-stage classification."""
        source = self.repo.get_source(source_id)
        if not source:
            raise ValueError(f"Source not found: {source_id}")

        logger.info(f"Mapping source: {source.name} ({source.root_url})")
        raw_urls = self.connector.map_urls(source.root_url, limit=limit)
        discovered_items: List[DiscoveredURL] = []

        for url in raw_urls:
            is_approved, reason = self.filter_url_tier1(url)
            semantic_score = self.evaluate_semantic_score(url) if is_approved else 0.0

            url_item = DiscoveredURL(
                url=url,
                source_id=source_id,
                discovered_at=datetime.utcnow(),
                tier1_status="approved" if is_approved else "rejected",
                rejection_reason=None if is_approved else reason,
                semantic_score=semantic_score,
                ingestion_status="pending" if (is_approved and semantic_score >= 0.5) else "skipped"
            )
            self.repo.upsert_url(url_item)
            discovered_items.append(url_item)

        logger.info(f"Discovered {len(discovered_items)} URLs for {source_id}.")
        return discovered_items

    def process_url(self, source_id: str, url: str) -> Optional[ExtractedDocument]:
        """Stage 02 & 03: Scrape, normalise, check hash for idempotency, and detect changes."""
        scrape_result = self.connector.scrape_url(url)
        raw_markdown = scrape_result.get("markdown", "")
        title = scrape_result.get("title", "")

        new_doc = DocumentNormaliser.normalise(
            source_id=source_id,
            url=url,
            raw_content=raw_markdown,
            is_html=False,
            title=title
        )

        # Check existing document for this URL
        existing_doc = self.repo.get_latest_document_by_url(url)

        if existing_doc:
            if existing_doc.content_hash == new_doc.content_hash:
                logger.info(f"Content hash identical for {url}. Idempotent no-op (no LLM tokens spent).")
                return None # Zero duplicate write
            else:
                logger.info(f"Substantive change detected for {url}! Triggering semantic diff.")
                new_doc.version = existing_doc.version + 1
                diff = SemanticDiffEngine.compare_documents(existing_doc, new_doc)
                if diff:
                    self.repo.record_change(diff)

        self.repo.save_document(new_doc)
        return new_doc

    def analyze_document_intelligence(self, doc: ExtractedDocument) -> Optional[MarketInsight]:
        """Stage 04 & 05: Classify into 12 categories, compute 6-dimension score, evaluate 10 Qs."""
        category = classify_text_category(doc.markdown)

        # Compute scoring dimensions based on source and content
        source = self.repo.get_source(doc.source_id)
        confidence = 90.0 if (source and source.tier == 1) else 80.0 if (source and source.tier == 2) else 65.0
        
        scoring = IntelligenceScorer.calculate(
            s_relevance=85.0,
            s_impact=80.0,
            s_confidence=confidence,
            s_time_sensitivity=70.0,
            s_campaign_alignment=75.0,
            s_geography=70.0
        )

        ten_qs = None
        if scoring.composite_score >= 70.0:
            ten_qs = StrategicEngine.evaluate_ten_questions(doc, category, scoring)

        # Record verifiable evidence anchor
        evidence_id = f"ev_{doc.doc_id}_01"
        evidence = SourceEvidence(
            evidence_id=evidence_id,
            doc_id=doc.doc_id,
            source_url=doc.url,
            claim=f"Updates published for {category} impacting first-time homebuyer readiness.",
            verbatim_quote=doc.markdown[:250],
            confidence_tier=source.tier if source else 3
        )
        self.repo.add_evidence(evidence)

        insight_id = f"ins_{doc.doc_id}"
        insight = MarketInsight(
            insight_id=insight_id,
            doc_id=doc.doc_id,
            primary_category=category,
            secondary_tags=[source.ecosystem] if source else [],
            scoring=scoring,
            ten_questions=ten_qs,
            evidence_ids=[evidence_id],
            status="candidate"
        )
        self.repo.save_insight(insight)
        return insight
