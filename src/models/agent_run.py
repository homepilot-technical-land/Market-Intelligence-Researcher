from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AgentRun(BaseModel):
    """Tracks execution history, queue metrics, token consumption, and performance."""
    run_id: str = Field(..., description="Unique run ID")
    agent_type: str = Field(..., description="source_driven, objective_driven, authority_discovery, diff_engine, grok_reasoning")
    queue_name: str = Field(default="default")
    status: str = Field(default="completed", description="pending, running, completed, failed, retried")
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    model_name: Optional[str] = None
    cost_usd: float = Field(default=0.0)
    duration_ms: int = Field(default=0)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
