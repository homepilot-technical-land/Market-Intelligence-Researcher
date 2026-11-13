from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ThreeRsDutyAllocation(BaseModel):
    """The 3 R's Framework in BPM: Allocating duties between automated bots and human intervention."""
    role: str = Field(default="Automated Pipeline Bot", description="Who performs the task: Bot (Firecrawl/Normaliser/Scorer/Grok) vs. Human Operator")
    rule: str = Field(default="Idempotent SHA-256 validation", description="What prerequisite condition or rule must be met before advancing")
    route: str = Field(default="Ingest -> Score -> Review Queue", description="Next sequence, queue, or handoff point in the value stream")
    requires_human_validation: bool = Field(default=False, description="True if human operator sign-off is mandatory")

class InfluencesOnPerceptions(BaseModel):
    """The Influences on Perceptions model: Factors shaping customer perception."""
    service_encounters: str = Field(default="", description="Specific interactions with service providers (brokers, banks, solicitors, HomePilot)")
    evidence_of_service: str = Field(default="", description="Tangible/intangible cues (checklists, scenario dashboards, reports)")
    price_value_perception: str = Field(default="", description="Perceived value for money (free tier vs. 90-Day Journey Pass vs. €25/mo)")
    brand_image: str = Field(default="", description="Reputation as Trusted Guide / Homeownership OS vs. generic mortgage calculator")

class BPMJourneyMapping(BaseModel):
    """Customer Journey Mapping (Alignment Diagram) within the homeownership value stream."""
    point_of_view: str = Field(default="", description="Perspective of the specific customer segment")
    journey_scope: str = Field(default="Aspiration to Closing", description="Scope: Pre-purchase, Active Purchase, Post-Purchase, Wealth Building")
    primary_stage: str = Field(default="Mortgage Planning", description="Current stage in the homebuyer value stream")
    moments_of_truth: List[str] = Field(default_factory=list, description="Vital emotional instances (e.g. Deposit target met, Bidding war lost, Loan offer received)")
    points_of_failure: List[str] = Field(default_factory=list, description="Bottlenecks and potential failure points (e.g. Valuation gap, stress-test failure, conveyancing delays)")
    duty_allocation: ThreeRsDutyAllocation = Field(default_factory=ThreeRsDutyAllocation, description="The 3 R's allocating duties between bots and human validation")

class AudiencePersona(BaseModel):
    """Dynamic Audience Persona & Behavioral Segment Model."""
    segment_id: str = Field(..., description="Unique segment identifier (e.g. seg_1_frustrated_ftb, dyn_commuter_renter_2026)")
    name: str = Field(..., description="Descriptive persona name")
    origin: str = Field(default="default_template", description="default_template, discovered_feed, or grok_reasoning")
    demographics: Dict[str, Any] = Field(default_factory=dict, description="Age, income bracket, household composition, location")
    
    # Psychographics & Emotional Transformation
    beliefs: List[str] = Field(default_factory=list)
    attitudes: List[str] = Field(default_factory=list)
    goals_aspirations: List[str] = Field(default_factory=list)
    fears: List[str] = Field(default_factory=list)
    current_state_of_mind: str = Field(default="", description="e.g. Confused, anxious, overwhelmed")
    desired_state_of_mind: str = Field(default="", description="e.g. Confident, in control, clear roadmap")
    
    # Behavioral & System Dynamics
    pain_points: List[str] = Field(default_factory=list)
    jobs_to_be_done: List[str] = Field(default_factory=list)
    system_bottlenecks: List[str] = Field(default_factory=list, description="Specific value stream constraints limiting this segment")
    mental_model_barriers: List[str] = Field(default_factory=list, description="Underlying cognitive biases (e.g. 'Mortgage-ready = homeownership-ready')")
    
    # BPM & Marketing Alignment
    influences_on_perceptions: InfluencesOnPerceptions = Field(default_factory=InfluencesOnPerceptions)
    journey_mapping: BPMJourneyMapping = Field(default_factory=BPMJourneyMapping)
    primary_hook: str = Field(default="", description="Strategic messaging hook addressing root cause")
    recommended_cta: str = Field(default="90-Day Buyer Journey Pass", description="Relevant HomePilot commercial offering or utility CTA")
    
    # Provenance & Dynamic Evolution
    discovered_from_source_ids: List[str] = Field(default_factory=list)
    evidence_citations: List[str] = Field(default_factory=list, description="Verbatim quotes from feeds substantiating this persona")
    confidence_score: float = Field(default=85.0, ge=0.0, le=100.0)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = Field(default=True)
