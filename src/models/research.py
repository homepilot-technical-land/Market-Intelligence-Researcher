from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ResearchObjective(BaseModel):
    """Represents an Objective-Driven Research topic initiated by HomePilot."""
    objective_id: str = Field(..., description="Unique objective ID (e.g. obj_ftb_financial_readiness)")
    title: str = Field(..., description="Strategic research question/objective")
    strategic_dimension: str = Field(..., description="financial_confidence, decision_intelligence, reduced_uncertainty, financial_outcomes, homeownership_journey")
    core_questions: List[str] = Field(default_factory=list, description="Sub-questions broken down for investigation")
    target_audiences: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchRun(BaseModel):
    """Tracks a single execution of an objective-driven research investigation."""
    run_id: str = Field(..., description="Unique run ID")
    objective_id: str = Field(..., description="Foreign key to research_objectives")
    sources_consulted: List[str] = Field(default_factory=list)
    findings_extracted_ids: List[str] = Field(default_factory=list)
    identified_gaps: List[str] = Field(default_factory=list)
    recommended_new_sources: List[str] = Field(default_factory=list)
    consolidated_report_markdown: str = Field(default="")
    status: str = Field(default="completed", description="in_progress, completed, failed")
    executed_at: datetime = Field(default_factory=datetime.utcnow)
