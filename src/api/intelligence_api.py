from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.storage.repository import IntelligenceRepository
from src.pipeline.runner import MarketIntelligencePipeline
from src.intelligence.authority_discovery import AuthoritySourceDiscoveryEngine
from src.intelligence.grok_service import GrokService
from src.models import ResearchObjective

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from src.api.middleware import (
    RFC7807Exception,
    rfc7807_http_exception_handler,
    rfc7807_validation_exception_handler,
    rfc7807_custom_exception_handler
)

repo = IntelligenceRepository()
pipeline = MarketIntelligencePipeline(repository=repo)
authority_engine = AuthoritySourceDiscoveryEngine(repository=repo)
grok_service = GrokService()

def bootstrap_data():
    if not repo.list_sources():
        pipeline.load_sources_from_registry()
    if not repo.list_candidate_sources():
        authority_engine.discover_and_evaluate_candidates()

@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_data()
    yield

app = FastAPI(
    title="HomePilot Market Intelligence Service",
    description="Python FastAPI Intelligence & Analytical Backend for HomePilot",
    version="1.0.0",
    lifespan=lifespan
)

# Register RFC 7807 Standard Exception Handlers
app.add_exception_handler(StarletteHTTPException, rfc7807_http_exception_handler)
app.add_exception_handler(RequestValidationError, rfc7807_validation_exception_handler)
app.add_exception_handler(RFC7807Exception, rfc7807_custom_exception_handler)

# Also ensure bootstrap for testing
bootstrap_data()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "intelligence_service",
        "database_connected": repo._connected,
        "firecrawl_configured": pipeline.connector.is_configured(),
        "grok_configured": grok_service.is_configured(),
        "total_sources_registered": len(repo.list_sources())
    }

@app.get("/sources")
def list_sources(ecosystem: Optional[str] = None):
    sources = repo.list_sources()
    if ecosystem:
        sources = [s for s in sources if s.ecosystem == ecosystem]
    return {"count": len(sources), "sources": [s.model_dump() for s in sources]}

@app.get("/sources/candidates")
def list_candidate_sources():
    candidates = repo.list_candidate_sources(status="pending_approval")
    return {"count": len(candidates), "candidates": [c.model_dump() for c in candidates]}

class ResearchObjectiveRequest(BaseModel):
    objective_id: str
    title: str
    strategic_dimension: str
    core_questions: List[str]

@app.post("/research/objectives")
def create_research_objective(req: ResearchObjectiveRequest):
    obj = ResearchObjective(
        objective_id=req.objective_id,
        title=req.title,
        strategic_dimension=req.strategic_dimension,
        core_questions=req.core_questions
    )
    repo.save_research_objective(obj)
    return {"status": "created", "objective": obj.model_dump()}

@app.post("/discovery/run/{source_id}")
def trigger_source_discovery(source_id: str, limit: int = Query(default=20, le=100)):
    try:
        urls = pipeline.run_source_discovery(source_id, limit=limit)
        return {
            "source_id": source_id,
            "discovered_count": len(urls),
            "approved_count": len([u for u in urls if u.tier1_status == "approved"]),
            "urls": [u.model_dump() for u in urls]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
