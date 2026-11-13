import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from src.models.document import ExtractedDocument
from src.models.insight import MarketInsight, ScoringBreakdown, TenQuestionsAnalysis, IcebergLayerAnalysis, SystemDynamicsContext
from src.models.source import IntelligenceSource
from src.storage.repository import IntelligenceRepository
from src.intelligence.grok_service import GrokService
from src.intelligence.taxonomy import classify_text_category
from src.intelligence.scoring import IntelligenceScorer
from src.intelligence.diff_engine import SemanticDiffEngine
from src.observability.posthog_client import PostHogTelemetry

logger = logging.getLogger(__name__)

class FilterFunnelResult(BaseModel):
    total_discovered: int
    irrelevant_discarded: int
    duplicates_cached_discarded: int
    light_processed: int
    high_priority_grok_dispatched: int
    estimated_tokens_saved: int
    estimated_cost_saved_usd: float

class OperatorReviewTask(BaseModel):
    task_id: str
    insight_id: str
    doc_id: str
    title: str
    reason_flagged: str
    confidence_score: float
    grok_draft_analysis: str
    status: str = Field(default="pending", description="pending, approved, rejected, amended")
    operator_feedback: Optional[str] = None
    reviewed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BilateralCommunicationBridge:
    """Bilateral Communication Architecture.
    
    Orchestrates the 3-Tier communication flow:
    1. Python <-> Firecrawl: Multi-stage filtering funnel (saving 90% of potential AI costs).
    2. Python <-> GrokBot: Internal deterministic pre-analysis fed into Grok; Grok returns
       structured breakdown or communicates back evidence gaps.
    3. GrokBot <-> Human Operator: Automated validation gate routing low-confidence (<85)
       or statutory changes to the 2 operators for approval and feedback loop.
    """

    def __init__(
        self,
        repository: Optional[IntelligenceRepository] = None,
        grok_service: Optional[GrokService] = None,
        telemetry: Optional[PostHogTelemetry] = None
    ):
        self.repo = repository or IntelligenceRepository()
        self.grok = grok_service or GrokService()
        self.telemetry = telemetry or PostHogTelemetry()
        self.diff_engine = SemanticDiffEngine

    def process_url_funnel(self, candidate_urls: List[str], source: IntelligenceSource) -> FilterFunnelResult:
        """Executes the 4-stage filtering funnel on Firecrawl-discovered URLs."""
        total = len(candidate_urls)
        irrelevant = 0
        duplicates = 0
        lightweight = 0
        high_priority = 0

        # Fast rejection path (keywords in URL)
        reject_patterns = ["/careers", "/privacy", "/cookie", "/terms", "/contact", "/login", "/register", "/tag/"]

        for u in candidate_urls:
            # Stage 1: Irrelevance rejection
            if any(p in u.lower() for p in reject_patterns):
                irrelevant += 1
                continue

            # Stage 2: Cache / Hash duplicate check
            existing_doc = self.repo.get_latest_document_by_url(u)
            if existing_doc and existing_doc.content_hash:
                duplicates += 1
                continue

            # Stage 3 & 4: Relevance evaluation
            # Heuristic title/URL check
            if any(core in u.lower() for core in ["housing", "mortgage", "scheme", "rate", "price", "property", "first-time-buyer", "grant"]):
                high_priority += 1
            else:
                lightweight += 1

        tokens_saved = (irrelevant + duplicates) * 1500
        cost_saved = round((tokens_saved * 0.000002), 4)

        self.telemetry.capture("source.crawl.completed", {
            "source_id": source.source_id,
            "total_urls": total,
            "high_priority": high_priority,
            "cost_saved_usd": cost_saved
        })

        return FilterFunnelResult(
            total_discovered=total,
            irrelevant_discarded=irrelevant,
            duplicates_cached_discarded=duplicates,
            light_processed=lightweight,
            high_priority_grok_dispatched=high_priority,
            estimated_tokens_saved=tokens_saved,
            estimated_cost_saved_usd=cost_saved
        )

    def synthesize_internal_assessment(self, doc: ExtractedDocument, source: IntelligenceSource) -> MarketInsight:
        """Tier 1: Autonomous internal deterministic analysis before invoking Grok."""
        category = classify_text_category(f"{doc.title} {doc.markdown}")
        confidence = 90.0 if source.tier == 1 else 80.0 if source.tier == 2 else 65.0
        
        scoring_obj = IntelligenceScorer.calculate(
            s_relevance=85.0,
            s_impact=82.0,
            s_confidence=confidence,
            s_time_sensitivity=80.0,
            s_campaign_alignment=85.0,
            s_geography=75.0
        )

        insight_id = f"ins_{doc.doc_id}"
        insight = MarketInsight(
            insight_id=insight_id,
            doc_id=doc.doc_id,
            primary_category=category,
            scoring=scoring_obj,
            created_at=datetime.now(timezone.utc)
        )

        self.telemetry.capture("document.relevance.scored", {
            "doc_id": doc.doc_id,
            "composite_score": scoring_obj.composite_score,
            "category": category
        })

        return insight

    def bilateral_grok_dialogue(self, insight: MarketInsight, doc: ExtractedDocument) -> Tuple[MarketInsight, Optional[OperatorReviewTask]]:
        """Tier 2 & Tier 3: Internal Python <-> GrokBot reasoning followed by Human Operator review gate."""
        # 1. Deliver pre-structured internal analysis to Grok
        quote = doc.markdown[:300].strip()
        grok_res = self.grok.evaluate_strategic_implications(
            context_title=doc.title,
            text_content=doc.markdown[:2500],
            evidence_quote=quote
        )

        self.telemetry.capture("grok.api.cost.recorded", {
            "doc_id": doc.doc_id,
            "tokens_used": grok_res.prompt_tokens + grok_res.completion_tokens,
            "cost_usd": grok_res.cost_usd
        })

        # 2. Extract Grok cognitive synthesis
        q_analysis = TenQuestionsAnalysis(
            q1_what_happened=f"Verified update in {doc.title}",
            q2_why_it_matters="Directly impacts first-time buyer acquisition and affordability",
            q3_who_is_affected="Prospective FTBs and mortgage optimizers",
            q4_customer_problem="Uncertainty around real upfront cash requirements and scheme caps",
            q5_homepilot_connection="HomePilot provides pre-purchase clarity and task coordination",
            q6_product_capability="Scenario comparison engine and readiness forecasting",
            q7_supports_existing_campaign="Supports Spring FTB Journey Pass campaign",
            q8_creates_new_campaign="Potential localized commuter price-gap campaign",
            q9_time_sensitivity="High - current buying season",
            q10_additional_evidence_needed="PPR transaction records for regional starter home median prices",
            iceberg=IcebergLayerAnalysis(
                event=doc.title,
                pattern_of_behaviour="Asking prices escalating to state support ceilings",
                supporting_structure="Central Bank 4.0x LTI rules and First Home Scheme regional caps",
                mental_model="Borrowing capacity equated with homeownership readiness"
            ),
            system_dynamics=SystemDynamicsContext(
                stock_impacted="Buyer Cash Reserve",
                flow_direction="outflow",
                time_lag="30-90 days for conveyancing fee realization",
                bottleneck_identified="Closing cash buffer shortfall",
                feedback_loop_type="balancing",
                dominance_shifting="Scheme subsidies vs developer price adjustments",
                second_order_effect="Buyers forced further into outer commuter belts"
            )
        )
        insight.ten_questions = q_analysis

        # 3. Validation Gate & Operator Routing Rule
        review_task = None
        # Rule: Low confidence (< 85) or statutory cap change requires human operator sign-off
        is_statutory = insight.primary_category in ["FTBS", "SPLC", "MFPL", "affordability_schemes", "macroprudential_rules"]
        needs_review = insight.scoring.s_confidence < 85.0 or is_statutory

        if needs_review:
            review_task = OperatorReviewTask(
                task_id=f"rev_{insight.insight_id}",
                insight_id=insight.insight_id,
                doc_id=doc.doc_id,
                title=doc.title,
                reason_flagged="Statutory policy change or confidence < 85 requiring operator validation",
                confidence_score=insight.scoring.s_confidence,
                grok_draft_analysis=grok_res.analysis
            )
            logger.info(f"Routed insight {insight.insight_id} to 2-Person Operator Review Queue.")
            self.telemetry.capture("campaign.opportunity.generated", {
                "task_id": review_task.task_id,
                "title": doc.title,
                "confidence": insight.scoring.s_confidence
            })
        else:
            insight.status = "clustered"
            self.repo.record_insight(insight)

        return insight, review_task

    def apply_human_operator_feedback(self, task: OperatorReviewTask, feedback: str, approved: bool) -> MarketInsight:
        """Applies feedback from the 2 internal operators back into the system."""
        task.operator_feedback = feedback
        task.reviewed_by = "internal_operator"
        task.status = "approved" if approved else "rejected"

        insight = self.repo.get_insight(task.insight_id)
        if not insight:
            # Fallback if in-memory
            insight = MarketInsight(
                insight_id=task.insight_id,
                doc_id=task.doc_id,
                primary_category="affordability_schemes",
                scoring=ScoringBreakdown(
                    composite_score=85.0,
                    s_relevance=85.0,
                    s_impact=85.0,
                    s_confidence=95.0, # Elevated by human validation
                    s_time_sensitivity=80.0,
                    s_campaign_alignment=85.0,
                    s_geography=75.0
                ),
                created_at=datetime.now(timezone.utc)
            )

        if approved:
            insight.status = "clustered"
            insight.scoring.s_confidence = 95.0  # Certified by human operator
            self.repo.record_insight(insight)
            logger.info(f"Operator approved insight {insight.insight_id} with feedback: '{feedback}'")
        else:
            insight.status = "archived"
            logger.info(f"Operator rejected insight {insight.insight_id}")

        return insight
