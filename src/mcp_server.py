"""HomePilot Market Intelligence MCP Server.

Exposes native Model Context Protocol (MCP) tools for external AI bots (GrokBot, Claude Desktop, Cursor)
to interrogate the Market Intelligence Researcher, pull live PPR/CSO data, search the 14 MongoDB collections,
and submit knowledge gaps without direct database credentials.
"""

import sys
import os
from pathlib import Path

# Ensure project root is always in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import logging
from typing import List, Dict, Any, Optional
from mcp.server.mcpserver import MCPServer

from src.storage.repository import IntelligenceRepository
from src.connectors.api_connectors import PropertyPriceRegisterConnector, CSOStatConnector
from src.connectors.firecrawl_connector import FirecrawlConnector
from src.intelligence.grok_service import GrokService
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.models.research import ResearchObjective
from src.models.asset import GeneratedAsset, AssetPayload

# Suppress standard logging to stdout to keep stdio MCP stream clean
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

server = MCPServer("HomePilot Market Intelligence")
repo = IntelligenceRepository()
ppr_conn = PropertyPriceRegisterConnector()
cso_conn = CSOStatConnector()
firecrawl_conn = FirecrawlConnector()
grok_svc = GrokService()
daily_gen = DailyBriefingGenerator(repository=repo)

@server.tool()
def get_county_market_benchmarks(county: str = "Meath") -> Dict[str, Any]:
    """Retrieve verified Property Price Register (PPR) starter & mover prices, CSO inflation rates, and statutory First Home Scheme price caps for an Irish county.
    
    Serves both First-Time Buyers (FTB) and Second-Time Buyers (STB / home movers).
    
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
    briefing = daily_gen.generate_morning_briefing(county_focus=county)
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

@server.tool()
def ask_research_engine(question: str, county: Optional[str] = "Meath") -> Dict[str, Any]:
    """Ask the HomePilot Market Intelligence Researcher a direct analytical question.
    The engine queries internal MongoDB evidence, live PPR pricing, and CSO inflation indicators to return a grounded assessment.
    
    Args:
        question: The analytical question or hypothesis to evaluate.
        county: Optional target Irish county (default 'Meath').
    """
    affordability = ppr_conn.calculate_county_affordability_benchmarks(county=county or "Meath")
    cso_data = cso_conn.fetch_housing_market_indicators()
    evidence = repo.list_evidence(limit=3)

    return {
        "question": question,
        "county": county,
        "verified_market_context": {
            "ppr_benchmarks": affordability,
            "cso_macro_indicators": cso_data,
            "sample_primary_evidence": [e.model_dump() for e in evidence]
        },
        "engine_guidance": "Use the verified market context above to answer. Adhere strictly to Rule B-02 (double citations) and Rule B-04 (dual human operator review)."
    }

@server.tool()
def scrape_web_url(url: str, only_main_content: bool = True) -> Dict[str, Any]:
    """Scrape and extract clean markdown content from an external web page using Firecrawl.
    
    Args:
        url: Full web URL to scrape.
        only_main_content: Whether to strip navigation, footers, and boilerplate (default True).
    """
    scrape_res = firecrawl_conn.scrape_url(url=url, only_main_content=only_main_content)
    return {
        "url": url,
        "title": scrape_res.get("title", ""),
        "markdown_content": scrape_res.get("markdown", "")[:5000],
        "status": scrape_res.get("status", 200)
    }

@server.tool()
def search_web_sources(query: str, limit: int = 3) -> Dict[str, Any]:
    """Execute a search-then-scrape query across live Irish housing and market sources using Firecrawl.
    
    Covers market policies, price changes, and regulatory guidelines for both First-Time Buyers and Second-Time Buyers.
    
    Args:
        query: Search query (e.g. 'Central Bank second time buyer mortgage rules', 'Help to Buy cap Meath').
        limit: Max search results to return (default 3).
    """
    results = firecrawl_conn.search(query=query, limit=limit)
    return {
        "query": query,
        "results_count": len(results),
        "results": results
    }

@server.tool()
def extract_social_thread(platform: str, url_or_query: str) -> Dict[str, Any]:
    """Extract discussions, community posts, and sentiment across social platforms:
    Reddit, Instagram, Facebook, and X (Twitter).
    
    Covers both First-Time Buyers (FTBs) and Second-Time Buyers (STBs / movers / trader-ups).
    
    Args:
        platform: Target platform ('reddit', 'x', 'facebook', 'instagram').
        url_or_query: Direct URL of the post/thread, or topic query.
    """
    platform_clean = platform.lower().strip()
    
    # 1. Reddit
    if "reddit" in platform_clean:
        if url_or_query.startswith("http"):
            clean_url = url_or_query.split("?")[0].rstrip("/")
            json_url = f"{clean_url}.json"
            try:
                import httpx
                headers = {"User-Agent": "HomePilot-Intelligence-Researcher/1.0 (contact: info@homepilot.ie)"}
                res = httpx.get(json_url, headers=headers, timeout=15.0)
                if res.status_code == 200:
                    data = res.json()
                    post_data = data[0]["data"]["children"][0]["data"]
                    comments_data = data[1]["data"]["children"]
                    comments = []
                    for c in comments_data[:10]:
                        if "body" in c.get("data", {}):
                            comments.append(c["data"]["body"][:500])
                    return {
                        "platform": "reddit",
                        "title": post_data.get("title", ""),
                        "subreddit": post_data.get("subreddit", ""),
                        "author": "[REDACTED_USER]",
                        "selftext": post_data.get("selftext", "")[:3000],
                        "comments_sample": comments,
                        "extraction_method": "reddit_direct_api"
                    }
            except Exception:
                pass
            
            scrape_res = firecrawl_conn.scrape_url(url=url_or_query, only_main_content=True)
            return {
                "platform": "reddit",
                "title": scrape_res.get("title", ""),
                "content": scrape_res.get("markdown", "")[:4000],
                "extraction_method": "firecrawl_scrape"
            }
        else:
            search_query = f"site:reddit.com/r/ireland OR site:reddit.com/r/irishpersonalfinance {url_or_query}"
            results = firecrawl_conn.search(query=search_query, limit=3)
            return {
                "platform": "reddit",
                "query": url_or_query,
                "discussions_found": results,
                "extraction_method": "firecrawl_search"
            }

    # 2. X / Twitter
    elif "x" in platform_clean or "twitter" in platform_clean:
        intel = grok_svc.synthesize_strategic_x_intelligence(topic=url_or_query)
        return {
            "platform": "x",
            "topic": url_or_query,
            "analysis": intel.analysis,
            "buyer_pain_points": intel.buyer_pain_points,
            "proposed_bot_communications": intel.proposed_bot_communications,
            "homepilot_product_alignment": intel.homepilot_product_alignment,
            "extraction_method": "xai_grok_native"
        }

    # 3. Facebook
    elif "facebook" in platform_clean or "fb" in platform_clean:
        if url_or_query.startswith("http"):
            scrape_res = firecrawl_conn.scrape_url(url=url_or_query, only_main_content=True)
            return {
                "platform": "facebook",
                "url": url_or_query,
                "content": scrape_res.get("markdown", "")[:3000],
                "extraction_method": "firecrawl_scrape"
            }
        else:
            fb_results = firecrawl_conn.search_facebook_communities(query=url_or_query, limit=3)
            return {
                "platform": "facebook",
                "query": url_or_query,
                "community_discussions": fb_results,
                "extraction_method": "firecrawl_facebook_community_search"
            }

    # 4. Instagram
    elif "instagram" in platform_clean or "insta" in platform_clean:
        if url_or_query.startswith("http"):
            actions = [FirecrawlConnector.build_wait_action(milliseconds=2000)]
            scrape_res = firecrawl_conn.scrape_url(url=url_or_query, only_main_content=True, actions=actions)
            return {
                "platform": "instagram",
                "url": url_or_query,
                "caption_and_metadata": scrape_res.get("markdown", "")[:3000],
                "extraction_method": "firecrawl_instagram_hydrate"
            }
        else:
            search_query = f"site:instagram.com {url_or_query} Irish property mortgage"
            results = firecrawl_conn.search(query=search_query, limit=3)
            return {
                "platform": "instagram",
                "query": url_or_query,
                "results": results,
                "extraction_method": "firecrawl_search"
            }

    else:
        return {"error": f"Unsupported platform: '{platform}'. Supported: 'reddit', 'x', 'facebook', 'instagram'."}

@server.tool()
def synthesize_x_discourse(
    topic: str,
    county: Optional[str] = None,
    buyer_type: str = "both"
) -> Dict[str, Any]:
    """Leverage xAI Grok to synthesize real-time social discourse, buyer pain points, and educational campaign angles on X.
    
    Supports both First-Time Buyers (FTB) and Second-Time Buyers (STB / home movers / trader-ups).
    
    Args:
        topic: Market friction, scheme name, or housing policy challenge.
        county: Optional target Irish commuter county (e.g. 'Meath', 'Kildare', 'Wicklow').
        buyer_type: Target buyer persona filter ('first_time_buyer', 'second_time_buyer', or 'both').
    """
    if buyer_type == "second_time_buyer":
        focus_topic = f"{topic} (focus: second-time buyers, home movers, trading up, negative equity, chain sales)"
    elif buyer_type == "first_time_buyer":
        focus_topic = f"{topic} (focus: first-time buyers, Help to Buy, First Home Scheme, starter homes)"
    else:
        focus_topic = f"{topic} (focus: both first-time buyers and second-time home movers)"
        
    intel = grok_svc.synthesize_strategic_x_intelligence(topic=focus_topic, county=county)
    return intel.model_dump()

if __name__ == "__main__":
    import argparse
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from mcp.server.transport_security import TransportSecuritySettings

    parser = argparse.ArgumentParser(description="HomePilot Market Intelligence MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http", "remote"],
        default="remote",
        help="MCP transport protocol ('remote' serves both SSE and Streamable HTTP with tunnel security enabled)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host interface (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8001")), help="Port for web/remote transport (default 8001 or $PORT)")
    args = parser.parse_args()

    if args.transport == "stdio":
        server.run(transport="stdio")
    elif args.transport == "sse":
        sec = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
            allowed_hosts=["*"],
            allowed_origins=["*"]
        )
        server.run(transport="sse", host=args.host, port=args.port, transport_security=sec)
    else:
        # Default 'remote' / 'streamable-http': Modern Streamable HTTP transport for Grok Connectors & Cloudflare
        sec = TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
            allowed_hosts=["*"],
            allowed_origins=["*"]
        )
        print(f"[*] Starting HomePilot Market Intelligence MCP Server on {args.host}:{args.port}")
        print(f"[*] Streamable HTTP endpoint: /mcp")
        server.run(transport="streamable-http", host=args.host, port=args.port, transport_security=sec)
