from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.storage.repository import IntelligenceRepository
from src.pipeline.runner import MarketIntelligencePipeline
from src.intelligence.authority_discovery import AuthoritySourceDiscoveryEngine
from src.intelligence.grok_service import GrokService
from src.models import ResearchObjective
from src.mcp_server import server as mcp_server
from mcp.server.transport_security import TransportSecuritySettings

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

# Configure MCP Server with tunnel/cloud security settings
mcp_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
    allowed_hosts=["*"],
    allowed_origins=["*"]
)
mcp_app = mcp_server.streamable_http_app(transport_security=mcp_security, host="0.0.0.0")

def bootstrap_data():
    if not repo.list_sources():
        pipeline.load_sources_from_registry()
    if not repo.list_candidate_sources():
        authority_engine.discover_and_evaluate_candidates()

@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_data()
    session_mgr = getattr(mcp_server._lowlevel_server, "_session_manager", None)
    if session_mgr and not getattr(session_mgr, "_has_started", False):
        async with session_mgr.run():
            yield
    else:
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

@app.get("/")
@app.head("/")
def root_health():
    """Root health probe for Cloud host probes (e.g. Render HEAD /)."""
    return {
        "status": "healthy",
        "service": "homepilot-market-intelligence",
        "mcp_endpoint": "/mcp"
    }

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

from fastapi.responses import HTMLResponse
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.connectors.api_connectors import PropertyPriceRegisterConnector, CSOStatConnector
from src.models.asset import GeneratedAsset, AssetPayload

daily_generator = DailyBriefingGenerator(repository=repo)
ppr_conn = PropertyPriceRegisterConnector()
cso_conn = CSOStatConnector()

@app.get("/briefings/latest")
def get_latest_briefing(county: str = "Meath"):
    """Returns latest compiled daily briefing for a county."""
    briefing = daily_generator.generate_briefing(county=county)
    return briefing.model_dump()

@app.get("/market/metrics/{county}")
def get_county_market_metrics(county: str):
    """Returns live PPR prices, CSO inflation benchmarks, and scheme caps."""
    affordability = ppr_conn.calculate_county_affordability_benchmarks(county=county)
    cso_data = cso_conn.fetch_housing_market_indicators()
    return {
        "county": county,
        "ppr_affordability_benchmarks": affordability,
        "cso_housing_indicators": cso_data
    }

class CampaignDraftRequest(BaseModel):
    title: str
    target_persona: str
    format: str  # x_thread, instagram_carousel, short_form_video_script, strategic_brief
    headline: str
    copy_body: str
    cited_evidence_ids: List[str]
    author: str = "GrokBot"

@app.post("/campaigns/blueprints")
def submit_campaign_blueprint(req: CampaignDraftRequest):
    """GrokBot submits drafted campaign blueprint into the Dual Operator Review Queue."""
    if len(req.cited_evidence_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Rule B-02 Violation: Campaign blueprints require at least 2 primary evidence citations."
        )
    import uuid
    asset_id = f"asset_{uuid.uuid4().hex[:8]}"
    asset = GeneratedAsset(
        asset_id=asset_id,
        campaign_id="camp_grok_bilateral",
        asset_type=req.format,
        content_payload=AssetPayload(
            headline=req.headline,
            copy_body=req.copy_body,
            evidence_citations=req.cited_evidence_ids
        ),
        review_status="pending_review"
    )
    repo.save_asset(asset)
    return {
        "status": "submitted_for_review",
        "asset_id": asset_id,
        "review_status": "pending_review",
        "notes": "Awaiting Dual Operator Review under Rule B-04."
    }

@app.post("/chat")
def chat_with_grok(message: str = Query(...), county: Optional[str] = "Meath"):
    """Bilateral conversational endpoint for GrokBot with live MongoDB context injection."""
    # Pull current market context
    market_metrics = ppr_conn.calculate_county_affordability_benchmarks(county=county or "Meath")
    cso_data = cso_conn.fetch_housing_market_indicators()
    
    context_prompt = (
        f"You are the HomePilot Market Strategist & FTB Advocate. You are communicating with the HomePilot team.\n"
        f"Current County: {county}\n"
        f"PPR Benchmarks: {market_metrics}\n"
        f"CSO Indicators: {cso_data}\n"
        f"Answer analytically, strictly citing empirical numbers and observing Rule B-02 and B-04."
    )
    res = grok_service.evaluate_strategic_implications(
        context_title=f"User Query: {message}",
        text_content=f"{context_prompt}\nUser Question: {message}",
        evidence_quote=message
    )
    return {
        "response": res.analysis,
        "model": res.model,
        "tokens": res.prompt_tokens + res.completion_tokens,
        "county": county
    }

@app.get("/chat", response_class=HTMLResponse)
def get_chat_interface():
    """Mobile & Desktop Responsive Web Chat Interface for GrokBot."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HomePilot GrokBot Desktop & Mobile Interface</title>
        <style>
            :root { --bg: #0d1117; --panel: #161b22; --border: #30363d; --text: #c9d1d9; --accent: #238636; --user: #1f6feb; }
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: var(--panel); border-bottom: 1px solid var(--border); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }
            header h1 { font-size: 16px; margin: 0; font-weight: 600; color: #58a6ff; }
            #chat-box { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
            .msg { max-width: 85%; padding: 12px 16px; border-radius: 8px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
            .grok { align-self: flex-start; background: var(--panel); border: 1px solid var(--border); }
            .user { align-self: flex-end; background: var(--user); color: #fff; }
            footer { background: var(--panel); border-top: 1px solid var(--border); padding: 14px 20px; display: flex; gap: 10px; }
            input[type="text"] { flex: 1; background: var(--bg); border: 1px solid var(--border); color: #fff; padding: 10px 14px; border-radius: 6px; font-size: 14px; outline: none; }
            button { background: var(--accent); color: #fff; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; }
            button:disabled { opacity: 0.5; cursor: not-allowed; }
            .meta { font-size: 11px; color: #8b949e; margin-top: 4px; }
        </style>
    </head>
    <body>
        <header>
            <h1>HomePilot GrokBot (Bilateral Interface)</h1>
            <span style="font-size: 12px; color: #3fb950;">● Connected to MongoDB: marketintelligenceresearch</span>
        </header>
        <div id="chat-box">
            <div class="msg grok">
                <strong>HomePilot GrokBot</strong><br>
                Welcome Samson. I am synchronized with the HomePilot Market Intelligence Engine. I have direct access to your 35 Irish property sources, PPR transaction price benchmarks, and CSO indicators. What market angle or county shall we examine?
            </div>
        </div>
        <footer>
            <input type="text" id="userInput" placeholder="Ask GrokBot about starter home prices, commuter trends, or draft a campaign..." autofocus>
            <button id="sendBtn" onclick="sendMessage()">Send</button>
        </footer>
        <script>
            const input = document.getElementById('userInput');
            const box = document.getElementById('chat-box');
            const btn = document.getElementById('sendBtn');

            input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });

            async function sendMessage() {
                const text = input.value.trim();
                if (!text) return;
                
                // Append user message
                const userDiv = document.createElement('div');
                userDiv.className = 'msg user';
                userDiv.textContent = text;
                box.appendChild(userDiv);
                input.value = '';
                btn.disabled = true;
                box.scrollTop = box.scrollHeight;

                // Placeholder bot message
                const grokDiv = document.createElement('div');
                grokDiv.className = 'msg grok';
                grokDiv.innerHTML = '<em>Thinking with live market context...</em>';
                box.appendChild(grokDiv);
                box.scrollTop = box.scrollHeight;

                try {
                    const res = await fetch(`/chat?message=${encodeURIComponent(text)}`, { method: 'POST' });
                    const data = await res.json();
                    grokDiv.innerHTML = `<strong>HomePilot GrokBot</strong><br>${data.response.replace(/\\n/g, '<br>')}<div class="meta">Model: ${data.model} | Tokens: ${data.tokens}</div>`;
                } catch (err) {
                    grokDiv.innerHTML = `<strong>Error</strong><br>Failed to reach GrokBot backend: ${err.message}`;
                } finally {
                    btn.disabled = false;
                    box.scrollTop = box.scrollHeight;
                }
            }
        </script>
    </body>
    </html>
    """

# Mount the MCP server routes (e.g. /mcp for Streamable HTTP)
app.mount("", mcp_app)
