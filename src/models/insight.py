from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ScoringBreakdown(BaseModel):
    composite_score: float = Field(..., ge=0.0, le=100.0)
    s_relevance: float = Field(..., ge=0.0, le=100.0, description="HomePilot Strategic Relevance (weight 0.25)")
    s_impact: float = Field(..., ge=0.0, le=100.0, description="Customer Financial Impact (weight 0.25)")
    s_confidence: float = Field(..., ge=0.0, le=100.0, description="Evidence Confidence (weight 0.20)")
    s_time_sensitivity: float = Field(..., ge=0.0, le=100.0, description="Time Sensitivity & Actionability (weight 0.15)")
    s_campaign_alignment: float = Field(..., ge=0.0, le=100.0, description="Active Campaign Alignment (weight 0.10)")
    s_geography: float = Field(..., ge=0.0, le=100.0, description="Geographic Specificity (weight 0.05)")

class IcebergLayerAnalysis(BaseModel):
    """The Iceberg Model: Unveiling root causes rather than merely reacting to events."""
    event: str = Field(..., description="Surface occurrence or announcement")
    pattern_of_behaviour: str = Field(..., description="Trends and recurring behaviours over time")
    supporting_structure: str = Field(..., description="Institutional rules, market mechanisms, and policies causing the pattern")
    mental_model: str = Field(..., description="Underlying buyer/lender assumptions, beliefs, and cognitive biases")

class SystemDynamicsContext(BaseModel):
    """Stocks, Flows, Bottlenecks, and Feedback Loops governing the market phenomenon."""
    stock_impacted: str = Field(..., description="System stock accumulating or draining (e.g. Buyer Cash Reserve, Housing Inventory)")
    flow_direction: str = Field(..., description="inflow, outflow, or buffer_depletion")
    time_lag: str = Field(..., description="Time delay between decision/event and real-world impact")
    bottleneck_identified: str = Field(..., description="The point of constraint in the homeownership value stream")
    feedback_loop_type: str = Field(..., description="balancing (stabilizing/cooling) or reinforcing (escalating/growth)")
    dominance_shifting: str = Field(..., description="Which competing feedback loop is taking control")
    second_order_effect: str = Field(..., description="Indirect, longer-term systemic consequence beyond first-order action")

class TenQuestionsAnalysis(BaseModel):
    """The 10 Strategic Questions grounded in dynamic systems thinking."""
    q1_what_happened: str
    q2_why_it_matters: str
    q3_who_is_affected: str
    q4_customer_problem: str
    q5_homepilot_connection: str
    q6_product_capability: str
    q7_supports_existing_campaign: str
    q8_creates_new_campaign: str
    q9_time_sensitivity: str
    q10_additional_evidence_needed: str
    iceberg: Optional[IcebergLayerAnalysis] = None
    system_dynamics: Optional[SystemDynamicsContext] = None

class MarketInsight(BaseModel):
    insight_id: str = Field(..., description="Unique insight ID")
    doc_id: str = Field(..., description="Foreign key to extracted_documents")
    primary_category: str = Field(..., description="One of the 12 strict taxonomy codes, e.g. FTBS, IRPM")
    secondary_tags: List[str] = Field(default_factory=list)
    geographic_entities: List[str] = Field(default_factory=list, description="e.g. ['County Meath', 'Navan']")
    scoring: ScoringBreakdown
    ten_questions: Optional[TenQuestionsAnalysis] = None
    evidence_ids: List[str] = Field(default_factory=list, description="Foreign keys to source_evidence")
    status: str = Field(default="candidate", description="candidate, clustered, archived")
    created_at: datetime = Field(default_factory=datetime.utcnow)
