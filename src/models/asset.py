from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AssetPayload(BaseModel):
    headline: str
    copy_body: str
    carousel_slides: Optional[List[Dict[str, Any]]] = None
    video_storyboard: Optional[List[Dict[str, Any]]] = None
    evidence_citations: List[str] = Field(default_factory=list)

class GeneratedAsset(BaseModel):
    asset_id: str = Field(..., description="Unique asset ID")
    campaign_id: str = Field(..., description="Foreign key to campaign_opportunities")
    asset_type: str = Field(..., description="x_thread, instagram_carousel, short_form_video_script, strategic_brief")
    content_payload: AssetPayload
    review_status: str = Field(default="pending_review", description="pending_review, approved, revisions_requested, rejected")
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    scheduled_publish_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
