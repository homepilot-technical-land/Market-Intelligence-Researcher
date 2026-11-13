"""HomePilot Market Intelligence MCP Server.

Exposes native Model Context Protocol (MCP) tools for external AI bots (GrokBot, Claude Desktop, Cursor)
to interrogate the Market Intelligence Researcher, pull live PPR/CSO data, search the 14 MongoDB collections,
and submit knowledge gaps without direct database credentials.
"""

import sys
import logging
from typing import List, Dict, Any, Optional
from mcp.server.mcpserver import MCPServer

from src.storage.repository import IntelligenceRepository
from src.connectors.api_connectors import PropertyPriceRegisterConnector, CSOStatConnector
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.models.research import ResearchObjective
from src.models.asset import GeneratedAsset, AssetPayload

# Suppress standard logging to stdout to keep stdio MCP stream clean
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

server = MCPServer("HomePilot Market Intelligence")
repo = IntelligenceRepository()
ppr_conn = PropertyPriceRegisterConnector()
cso_conn = CSOStatConnector()
daily_gen = DailyBriefingGenerator(repository=repo)

@server.tool()
def get_county_market_benchmarks(county: str = "Meath") -> Dict[str, Any]:
    """Retrieve verified Property Price Register (PPR) starter prices, CSO inflation rates, and statutory First Home Scheme price caps for an Irish county.
    
    Args:
        county: Irish county name (e.g. 'Meath', 'Kildare', 'Wicklow', 'Dublin').
    """
    affordability = ppr_conn.calculate_county_affordability_benchmarks(county=county)
    cso_data = cso_conn.fetch_housing_market_indicators()
    return {
        "county": county,
        "ppr_affordability_benchmarks": affordability,
        "cso_housing_indicators": cso_data
    }

@server.tool()
def get_latest_daily_briefing(county: str = "Meath") -> Dict[str, Any]:
    """Fetch the latest compiled morning intelligence briefing for an Irish commuter county, synthesized from live sources and price trends.
    
    Args:
        county: Irish county name (e.g. 'Meath', 'Kildare', 'Wicklow').
    """
    briefing = daily_gen.generate_briefing(county=county)
    return briefing.model_dump()

@server.tool()
def search_evidence_pool(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search verified ground-truth quotations, data points, and ingested documents stored in the 14-collection MongoDB database.
    
    Args:
        query: Search term (e.g. 'First Home Scheme cap', 'booking deposit forfeit', 'conveyancing timeline').
        limit: Max number of evidence records to return (default 5).
    """
    evidence_records = repo.list_evidence(limit=limit)
    return [e.model_dump() for e in evidence_records]

@server.tool()
def submit_knowledge_gap(topic: str, questions: List[str]) -> Dict[str, Any]:
    """Submit an unanswered market question or missing policy wire into the research backlog. The autonomous background crawler will schedule a targeted crawl to resolve this gap.
    
    Args:
        topic: The specific market friction or policy area lacking data.
        questions: Specific questions to be investigated by the crawler.
    """
    import uuid
    obj_id = f"gap_{uuid.uuid4().hex[:8]}"
    obj = ResearchObjective(
        objective_id=obj_id,
        title=topic,
        strategic_dimension="knowledge_gap_backlog",
        core_questions=questions
    )
    repo.save_research_objective(obj)
    return {
        "status": "queued_for_crawler",
        "objective_id": obj_id,
        "message": "Knowledge gap recorded. The autonomous scheduler daemon will dispatch a targeted crawl to resolve this."
    }

@server.tool()
def submit_campaign_blueprint(
    title: str,
    format: str,
    headline: str,
    copy_body: str,
    citations: List[str]
) -> Dict[str, Any]:
    """Submit a drafted campaign blueprint (X Thread, Carousel, Video Script, Brief) into the Dual Operator Review Queue under Rule B-04.
    
    Args:
        title: Working title of the campaign.
        format: Asset format ('x_thread', 'instagram_carousel', 'short_form_video_script', 'strategic_brief').
        headline: Main hook or primary headline.
        copy_body: Full body copy or slide scripts.
        citations: List of at least TWO primary evidence citations (Rule B-02).
    """
    if len(citations) < 2:
        return {
            "status": "rejected_by_rule_b02",
            "error": "Rule B-02 Violation: Campaign blueprints require at least 2 primary evidence citations before submission."
        }
    import uuid
    asset_id = f"asset_{uuid.uuid4().hex[:8]}"
    asset = GeneratedAsset(
        asset_id=asset_id,
        campaign_id="camp_grok_mcp",
        asset_type=format,
        content_payload=AssetPayload(
            headline=headline,
            copy_body=copy_body,
            evidence_citations=citations
        ),
        review_status="pending_review"
    )
    repo.save_asset(asset)
    return {
        "status": "submitted_for_operator_review",
        "asset_id": asset_id,
        "review_status": "pending_review",
        "message": "Asset submitted to Dual Operator Review Queue. Awaiting sign-off under Rule B-04."
    }

if __name__ == "__main__":
    # Default stdio transport for local desktop MCP clients
    server.run(transport="stdio")
