from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SourceCandidate(BaseModel):
    """Represents a candidate authoritative Irish source discovered by the Authority Source Discovery Engine."""
    candidate_id: str = Field(..., description="Unique ID (e.g. cand_cso_housing)")
    name: str = Field(..., description="Entity or organisation name")
    root_url: str = Field(..., description="Target domain or endpoint")
    ecosystem: str = Field(..., description="Intelligence ecosystem")
    publisher_identity: str = Field(..., description="e.g. Statutory Agency, Independent Research, Industry Body")
    authority_score: float = Field(..., ge=0.0, le=100.0, description="Calculated authority rating")
    justification: str = Field(..., description="Why this source fills an identified HomePilot research gap")
    identified_gap: str = Field(..., description="e.g. Regional affordability, household expenditure, rent index")
    review_status: str = Field(default="pending_approval", description="pending_approval, approved, rejected, deferred")
    reviewer_notes: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
