from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class FirecrawlConfig(BaseModel):
    mode: str = Field(default="map_then_crawl", description="map, crawl, map_then_crawl, scrape")
    max_depth: int = Field(default=2, ge=1, le=5)
    page_limit: int = Field(default=100, ge=1, le=1000)
    include_paths: List[str] = Field(default_factory=list)
    exclude_paths: List[str] = Field(default_factory=list)

class RateLimitConfig(BaseModel):
    requests_per_minute: int = Field(default=10, ge=1, le=60)
    respect_robots_txt: bool = Field(default=True)

class IntelligenceSource(BaseModel):
    source_id: str = Field(..., description="Unique alphanumeric identifier")
    name: str = Field(..., description="Human-readable organisation name")
    root_url: str = Field(..., description="Root URL of the source")
    ecosystem: str = Field(..., description="One of the 6 intelligence ecosystems")
    tier: int = Field(default=3, ge=1, le=4, description="1=Statutory, 2=Institutional, 3=Portal/Developer, 4=Media")
    connector_type: str = Field(default="firecrawl", description="firecrawl or api_or_dataset")
    cadence: str = Field(default="daily", description="hourly_12, daily, weekly, on_release")
    discovery: Optional[dict] = Field(default=None)
    firecrawl_config: Optional[FirecrawlConfig] = None
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    tags: List[str] = Field(default_factory=list)
    last_crawled_at: Optional[datetime] = None
    active: bool = Field(default=True)
