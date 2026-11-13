from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CampaignOpportunity(BaseModel):
    campaign_id: str = Field(..., description="Unique campaign ID")
    theme_title: str = Field(..., description="e.g. 'Are You Financially Ready to Own a Home?'")
    strategic_dimension: str = Field(..., description="financial_confidence, decision_intelligence, reduced_uncertainty, financial_outcomes, homeownership_journey")
    target_segment: str = Field(default="seg_1_frustrated_ftb", description="One of the 5 granular audience segments")
    five_s_focus: str = Field(default="save", description="sell, serve, speak, save, or sizzle")
    storytelling_framework: str = Field(default="before_after_bridge", description="before_after_bridge, troublemaker, future_pacing")
    central_customer_problem: str = Field(..., description="Core homebuyer friction or knowledge gap")
    homepilot_positioning_hook: str = Field(..., description="Shifts perception from mortgage calculator to Homeownership OS")
    jargon_free_message: str = Field(default="", description="Human, encouraging, educational copy without banking jargon")
    commercial_offering_cta: str = Field(default="90-Day Buyer Journey Pass", description="e.g. 90-Day Journey Pass, Free Readiness Score, Premium")
    insight_ids: List[str] = Field(default_factory=list, description="Foreign keys to market_insights")
    status: str = Field(default="draft", description="draft, ready_for_review, approved, published, rejected")
    created_at: datetime = Field(default_factory=datetime.utcnow)
