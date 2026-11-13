import hashlib
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ExtractedDocument(BaseModel):
    doc_id: str = Field(..., description="Unique document ID (e.g. source_id_hash)")
    source_id: str = Field(..., description="Foreign key to intelligence_sources")
    url: str = Field(..., description="Source page URL")
    title: str = Field(default="", description="Page title")
    published_at: Optional[datetime] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    content_hash: str = Field(default="", description="SHA-256 hash of clean markdown content")
    markdown: str = Field(..., description="Extracted clean markdown payload")
    http_status: int = Field(default=200)
    author: Optional[str] = None
    version: int = Field(default=1, ge=1)
    is_active: bool = Field(default=True)

    @classmethod
    def create(cls, source_id: str, url: str, markdown: str, title: str = "", published_at: Optional[datetime] = None, version: int = 1):
        content_hash = hashlib.sha256(markdown.strip().encode("utf-8")).hexdigest()
        doc_id = f"{source_id}_{hashlib.md5(url.encode('utf-8')).hexdigest()[:10]}_v{version}"
        return cls(
            doc_id=doc_id,
            source_id=source_id,
            url=url,
            title=title,
            published_at=published_at,
            retrieved_at=datetime.utcnow(),
            content_hash=content_hash,
            markdown=markdown,
            version=version,
            is_active=True
        )
