import hashlib
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class DiscoveredURL(BaseModel):
    url: str = Field(..., description="Full canonical URL")
    url_hash: str = Field(default="", description="MD5 hash of the normalized URL")
    source_id: str = Field(..., description="Foreign key to intelligence_sources")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    path_depth: int = Field(default=1, ge=0)
    tier1_status: str = Field(default="approved", description="approved or rejected")
    rejection_reason: Optional[str] = None
    semantic_score: float = Field(default=0.0, ge=0.0, le=1.0)
    ingestion_status: str = Field(default="pending", description="pending, extracted, failed, skipped")
    last_checked_at: Optional[datetime] = None

    def model_post_init(self, __context):
        if not self.url_hash:
            self.url_hash = hashlib.md5(self.url.strip().lower().encode("utf-8")).hexdigest()
