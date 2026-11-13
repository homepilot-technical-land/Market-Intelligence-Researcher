from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SemanticDelta(BaseModel):
    summary: str = Field(..., description="High-level summary of semantic changes")
    added_facts: List[str] = Field(default_factory=list)
    removed_facts: List[str] = Field(default_factory=list)
    numeric_deltas: List[Dict[str, Any]] = Field(default_factory=list, description="e.g. [{'metric': 'interest_rate', 'old': 3.75, 'new': 3.45}]")

class ContentChange(BaseModel):
    change_id: str = Field(..., description="Unique change ID")
    doc_id: str = Field(..., description="Foreign key to extracted_documents")
    url: str = Field(..., description="Source URL")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    previous_hash: str = Field(...)
    current_hash: str = Field(...)
    change_type: str = Field(..., description="fact_change, policy_revision, pricing_update, date_change, trivial_layout")
    semantic_delta: SemanticDelta
    processed_for_insights: bool = Field(default=False)
