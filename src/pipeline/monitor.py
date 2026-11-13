import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.storage.repository import IntelligenceRepository
from src.connectors.firecrawl_connector import FirecrawlConnector
from src.normalisation.normaliser import DocumentNormaliser
from src.intelligence.diff_engine import SemanticDiffEngine
from src.intelligence.strategic_engine import StrategicEngine
from src.intelligence.persona_engine import DynamicPersonaEngine
from src.intelligence.scoring import IntelligenceScorer
from src.models import (
    ExtractedDocument,
    ContentChange,
    MarketInsight,
    SourceEvidence,
    DiscoveredURL
)

logger = logging.getLogger("FeedMonitor")

class FeedMonitoringPipeline:
    """Phase 2 Operational Monitor: Scheduled Ingestion, Change Detection & Dynamic Persona Tracking."""

    def __init__(
        self,
        repository: Optional[IntelligenceRepository] = None,
        connector: Optional[FirecrawlConnector] = None
    ):
        self.repo = repository or IntelligenceRepository()
        self.connector = connector or FirecrawlConnector()
        self.persona_engine = DynamicPersonaEngine(repository=self.repo)

    def execute_scheduled_monitor_cycle(self, source_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Executes a full Phase 2 monitoring run across registered sources."""
        sources = self.repo.list_sources()
        if source_ids:
            sources = [s for s in sources if s.source_id in source_ids]

        results = {
            "sources_checked": len(sources),
            "documents_processed": 0,
            "idempotent_no_ops": 0,
            "semantic_changes_detected": 0,
            "insights_generated": 0,
            "dynamic_personas_discovered": 0
        }

        for source in sources:
            logger.info(f"Checking feed: {source.name} [{source.source_id}] ({source.cadence})")
            
            # Map top URLs
            discovered_urls = self.connector.map_urls(source.root_url, limit=10)
            
            for url in discovered_urls:
                # Filter out obvious non-content
                if any(x in url.lower() for x in ["/privacy", "/cookie", "/career", "/terms"]):
                    continue

                scrape_data = self.connector.scrape_url(url)
                raw_markdown = scrape_data.get("markdown", "")
                title = scrape_data.get("title", "")
                
                new_doc = DocumentNormaliser.normalise(
                    source_id=source.source_id,
                    url=url,
                    raw_content=raw_markdown,
                    is_html=False,
                    title=title
                )
                results["documents_processed"] += 1

                existing_doc = self.repo.get_latest_document_by_url(url)

                if existing_doc:
                    if existing_doc.content_hash == new_doc.content_hash:
                        results["idempotent_no_ops"] += 1
                        continue # Idempotent no-op: zero LLM cost
                    else:
                        logger.info(f"Substantive change detected on {url}")
                        results["semantic_changes_detected"] += 1
                        new_doc.version = existing_doc.version + 1
                        diff = SemanticDiffEngine.compare_documents(existing_doc, new_doc)
                        if diff:
                            self.repo.record_change(diff)

                self.repo.save_document(new_doc)

                # Evaluate for Dynamic Persona Evolution
                discovered_persona = self.persona_engine.evaluate_feed_for_persona_discovery(new_doc)
                if discovered_persona and discovered_persona.origin == "discovered_feed":
                    results["dynamic_personas_discovered"] += 1

                # Generate Systems Dynamics Insight
                scoring = IntelligenceScorer.calculate(
                    s_relevance=88.0,
                    s_impact=82.0,
                    s_confidence=90.0 if source.tier <= 2 else 70.0,
                    s_time_sensitivity=75.0,
                    s_campaign_alignment=80.0,
                    s_geography=80.0
                )

                if scoring.composite_score >= 70.0:
                    ten_qs = StrategicEngine.evaluate_ten_questions(new_doc, "FTBS", scoring)
                    evidence_id = f"ev_{new_doc.doc_id}"
                    self.repo.add_evidence(SourceEvidence(
                        evidence_id=evidence_id,
                        doc_id=new_doc.doc_id,
                        source_url=new_doc.url,
                        claim=f"Verified feed development for {source.name}",
                        verbatim_quote=new_doc.markdown[:200],
                        confidence_tier=source.tier
                    ))
                    
                    insight = MarketInsight(
                        insight_id=f"ins_{new_doc.doc_id}",
                        doc_id=new_doc.doc_id,
                        primary_category="FTBS",
                        scoring=scoring,
                        ten_questions=ten_qs,
                        evidence_ids=[evidence_id],
                        status="candidate"
                    )
                    self.repo.save_insight(insight)
                    results["insights_generated"] += 1

        logger.info(f"Phase 2 Monitoring Cycle Complete: {results}")
        return results
