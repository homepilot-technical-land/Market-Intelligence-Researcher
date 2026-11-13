from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SourceEvidence(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence ID")
    doc_id: str = Field(..., description="Foreign key to extracted_documents")
    source_url: str = Field(..., description="Original URL anchor")
    claim: str = Field(..., description="Asserted market fact or statement")
    verbatim_quote: str = Field(..., description="Exact textual quote from the source document")
    data_points: Dict[str, Any] = Field(default_factory=dict, description="Extracted numerical or categorical parameters")
    confidence_tier: int = Field(default=3, ge=1, le=4, description="1=Statutory, 2=Institutional, 3=Portal, 4=Media")
    verified_by_human: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
