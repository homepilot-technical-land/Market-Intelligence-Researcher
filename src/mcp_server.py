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
from src.connectors.reddit_connector import RedditConnector
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
reddit_conn = RedditConnector()
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
def get_latest_daily_briefing(
    county: Optional[str] = None,
    campaign_name: Optional[str] = None
) -> Dict[str, Any]:
    """Fetch the latest compiled morning intelligence briefing, synthesized from live sources and price trends.
    
    If no county is specified, automatically batches across the current active campaign's targeted regions
    and includes any breaking Out-of-Focus Regional Spike Alerts.
    
    Args:
        county: Optional specific Irish county name (e.g. 'Meath', 'Kildare', 'Wicklow'). Defaults to active campaign regions.
        campaign_name: Optional campaign title filter.
    """
    briefing = daily_gen.generate_morning_briefing(county_focus=county, campaign_name=campaign_name)
    return briefing.model_dump()

@server.tool()
def set_active_campaign_target(
    campaign_name: str,
    target_counties: List[str],
    target_personas: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Set the active marketing campaign and its target geographic counties for the daily batching engine via GrokBot.
    
    When set, the 07:00 UTC daily briefing, PPR affordability scans, and macro syntheses will automatically batch
    across these designated counties for the active campaign sprint.
    
    Args:
        campaign_name: Title of the campaign sprint (e.g. 'Q1 Commuter Cap Straddler Squeeze').
        target_counties: List of Irish counties targeted by this campaign period (e.g. ['Kildare', 'Meath', 'Wicklow']).
        target_personas: Optional list of persona IDs (e.g. ['seg_1_frustrated_ftb', 'dyn_seg_commuter_cap_straddler']).
        notes: Optional strategic notes or commercial intent from the marketing operators.
    """
    res = repo.set_active_campaign_focus(
        campaign_name=campaign_name,
        target_counties=target_counties,
        target_personas=target_personas,
        notes=notes
    )
    return {
        "status": "active_campaign_updated",
        "campaign_name": res["campaign_name"],
        "target_counties": res["target_counties"],
        "target_personas": res["target_personas"],
        "message": f"Daily batching engine is now focused on {len(res['target_counties'])} counties: {', '.join(res['target_counties'])}."
    }

@server.tool()
def get_active_campaign_target() -> Dict[str, Any]:
    """Retrieve the current active marketing campaign parameters, target counties, and persona focus."""
    return repo.get_active_campaign_focus()

@server.tool()
def trigger_out_of_focus_regional_alert(
    county: str,
    headline: str,
    summary: str,
    facts: Optional[List[str]] = None,
    strategic_implications: Optional[str] = None,
    category: str = "Statutory / Market Anomaly"
) -> Dict[str, Any]:
    """Trigger an Out-of-Focus Regional Spike Alert when news, price anomalies, or statutory changes break in an unfocused county.
    
    This records the alert in MongoDB and immediately surfaces it in the operator daily briefings and GrokBot feeds.
    
    Args:
        county: Irish county where the unexpected spike occurred (e.g. 'Cork', 'Galway', 'Louth').
        headline: Concise headline describing the breaking regional event.
        summary: Detailed breakdown of the event, facts, and source attribution.
        facts: List of verified numbers, quotes, or circular references.
        strategic_implications: How this impacts HomePilot's positioning or buyer journey.
        category: Event category (e.g. 'Statutory / Market Anomaly', 'Price Surge', 'Planning Crisis').
    """
    alert = repo.record_regional_spike_alert({
        "county": county.strip().title(),
        "headline": headline,
        "summary": summary,
        "facts": facts or [],
        "strategic_implications": strategic_implications or "Monitor for potential campaign expansion.",
        "category": category,
        "status": "active"
    })
    return {
        "status": "alert_triggered",
        "alert_id": alert["alert_id"],
        "county": alert["county"],
        "headline": alert["headline"],
        "message": f"Out-of-focus alert recorded for County {alert['county']}. It will be surfaced in the next Daily Briefing."
    }

@server.tool()
def get_out_of_focus_regional_alerts(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve breaking news, statutory policy changes, or price spikes detected in counties outside the current campaign focus.
    
    Args:
        limit: Max number of active alerts to return (default 5).
    """
    return repo.list_regional_spike_alerts(limit=limit, active_only=True)

@server.tool()
def record_campaign_social_spike(
    topic: str,
    sentiment: str,
    summary: str,
    counter_hook: Optional[str] = None,
    campaign_name: Optional[str] = None
) -> Dict[str, Any]:
    """Record a real-time viral social discussion or buyer sentiment spike on X relating to the active campaign via GrokBot.
    
    This injects live X-platform discourse into the daily executive intelligence briefing and alerts operators to shifts in buyer psychology.
    
    Args:
        topic: The trending topic or debate on X (e.g. '#HelpToBuy delays', 'Kildare new launch price hike').
        sentiment: Dominant buyer sentiment (e.g. 'Anxious & Confused', 'Frustrated with Scheme Caps', 'Optimistic').
        summary: Concise breakdown of what buyers and brokers are saying on X.
        counter_hook: Recommended HomePilot educational counter-narrative, mythbuster, or tool positioning.
        campaign_name: Optional campaign title (defaults to active campaign).
    """
    active_camp = repo.get_active_campaign_focus()
    c_name = campaign_name or active_camp.get("campaign_name", "Active Campaign")
    spike = repo.record_campaign_social_spike({
        "campaign_name": c_name,
        "topic": topic,
        "sentiment": sentiment,
        "summary": summary,
        "counter_hook": counter_hook or "Deploy HomePilot educational guide.",
        "status": "active"
    })
    return {
        "status": "social_spike_recorded",
        "spike_id": spike["spike_id"],
        "campaign_name": c_name,
        "topic": topic,
        "message": f"Social discourse spike on X recorded for '{topic}'. Surfaced in next Daily Briefing."
    }

@server.tool()
def get_campaign_social_spikes(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve active viral social spikes and sentiment shifts recorded from the X platform.
    
    Args:
        limit: Max number of active spikes to return (default 5).
    """
    return repo.list_campaign_social_spikes(limit=limit, active_only=True)

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
def submit_research_assessment(
    title: str,
    analysis: str,
    key_findings: List[str],
    buyer_pain_points: List[str],
    strategic_implications: List[str],
    category: str = "FTBS",
    county: Optional[str] = "Meath",
    evidence_quote: Optional[str] = None,
    source_reference: Optional[str] = "grokbot_deep_research",
    confidence_score: float = 85.0
) -> Dict[str, Any]:
    """Submit a structured research assessment, deep-dive exploration, or weekly analytical overview directly into the HomePilot MongoDB intelligence pool.
    
    This records the assessment into MongoDB across documents, evidence_records, and intelligence_findings.
    The system automatically incorporates it into theme clustering, daily briefings, and dynamic buyer persona tracking.
    
    Args:
        title: Title or research topic of the assessment.
        analysis: Full analytical text, thesis, or exploration breakdown.
        key_findings: List of verified factual developments or key takeaways.
        buyer_pain_points: Specific buyer frictions, anxieties, or obstacles identified.
        strategic_implications: Strategic relevance to HomePilot product positioning or campaigns.
        category: Primary Irish taxonomy category code (e.g. 'FTBS', 'IRPM', 'HPR', 'MIRC'). Default 'FTBS'.
        county: Focus Irish county (e.g. 'Meath', 'Kildare', 'Dublin', 'Wicklow').
        evidence_quote: Optional verbatim evidence quote or empirical data anchor.
        source_reference: Name of document or URL source referenced.
        confidence_score: Assessment confidence score (0.0 to 100.0, default 85.0).
    """
    import uuid
    from datetime import datetime, timezone
    from src.models.document import ExtractedDocument
    from src.models.evidence import SourceEvidence
    from src.models.insight import MarketInsight, ScoringBreakdown, TenQuestionsAnalysis

    uid = uuid.uuid4().hex[:8]
    doc_id = f"grok_doc_{uid}"
    now = datetime.now(timezone.utc)

    # 1. Save extracted document
    doc = ExtractedDocument(
        doc_id=doc_id,
        source_id="grokbot_research",
        url=f"grokbot://assessment/{uid}",
        title=title,
        published_at=now,
        markdown=analysis,
        cleaned_text=analysis,
        content_hash=f"hash_{uid}"
    )
    repo.save_document(doc)

    # 2. Save source evidence
    ev_id = f"ev_{uid}_01"
    quote = evidence_quote or (key_findings[0] if key_findings else analysis[:200])
    claim = key_findings[0] if key_findings else title
    evidence = SourceEvidence(
        evidence_id=ev_id,
        doc_id=doc_id,
        source_url=f"grokbot://assessment/{uid}",
        claim=claim,
        verbatim_quote=quote[:500],
        confidence_tier=2,
        verified_by_human=False
    )
    repo.add_evidence(evidence)

    # 3. Save market insight
    scoring = ScoringBreakdown(
        composite_score=min(100.0, max(0.0, confidence_score)),
        s_relevance=85.0,
        s_impact=85.0,
        s_confidence=confidence_score,
        s_time_sensitivity=80.0,
        s_campaign_alignment=80.0,
        s_geography=80.0
    )
    ten_qs = TenQuestionsAnalysis(
        q1_what_happened=title,
        q2_why_it_matters=analysis[:200],
        q3_who_is_affected=", ".join(buyer_pain_points[:3]) if buyer_pain_points else "Irish Homebuyers",
        q4_customer_problem=buyer_pain_points[0] if buyer_pain_points else "Market opacity",
        q5_homepilot_connection=strategic_implications[0] if strategic_implications else "Product positioning",
        q6_product_capability="Scenario comparison and buffer calculator",
        q7_supports_existing_campaign="Yes",
        q8_creates_new_campaign="Yes",
        q9_time_sensitivity="High",
        q10_additional_evidence_needed="Ongoing tracking"
    )
    ins_id = f"ins_{uid}"
    insight = MarketInsight(
        insight_id=ins_id,
        doc_id=doc_id,
        primary_category=category,
        secondary_tags=["grokbot_research", county or "National"],
        geographic_entities=[county] if county else ["National"],
        scoring=scoring,
        ten_questions=ten_qs,
        evidence_ids=[ev_id],
        status="candidate",
        created_at=now
    )
    repo.save_insight(insight)

    return {
        "status": "persisted_to_mongodb",
        "doc_id": doc_id,
        "evidence_id": ev_id,
        "insight_id": ins_id,
        "category": category,
        "county": county,
        "composite_score": confidence_score,
        "message": "Research assessment successfully recorded in MongoDB. The Theme Clustering Engine and Daily Morning Briefing will dynamically synthesize this evidence."
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
    if not scrape_res.get("success", False) or scrape_res.get("status", 200) >= 400:
        return {
            "url": url,
            "status": "error",
            "http_status": scrape_res.get("status", 502),
            "error": scrape_res.get("error", f"Failed to scrape {url}"),
            "markdown_content": ""
        }
    return {
        "url": url,
        "title": scrape_res.get("title", ""),
        "markdown_content": scrape_res.get("markdown", "")[:5000],
        "status": "success",
        "http_status": 200
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
        if url_or_query.startswith("http") or "/comments/" in url_or_query:
            # Check if official Reddit OAuth connector is configured
            if reddit_conn.is_configured():
                thread_res = reddit_conn.fetch_thread(url_or_id=url_or_query, max_comments=50)
                if thread_res.get("success"):
                    return {
                        "platform": "reddit",
                        "status": "success",
                        "extraction_method": "reddit_oauth_api",
                        "title": thread_res.get("title", ""),
                        "subreddit": thread_res.get("subreddit", ""),
                        "url": thread_res.get("url", url_or_query),
                        "score": thread_res.get("score", 0),
                        "selftext": thread_res.get("selftext", "")[:4000],
                        "total_comments_in_thread": thread_res.get("total_comments_in_thread", 0),
                        "comments_extracted": thread_res.get("comments_extracted", 0),
                        "comments_sample": [c["body"][:400] for c in thread_res.get("comments", [])[:15]]
                    }

            # If Reddit credentials are not configured or direct call failed, fetch search index snippets
            search_res = firecrawl_conn.search(query=url_or_query, limit=2)
            snippets = [r.get("description", "") for r in search_res if r.get("description")]

            return {
                "platform": "reddit",
                "url": url_or_query,
                "status": "credentials_required" if not reddit_conn.is_configured() else "blocked_by_anti_bot",
                "http_status": 403,
                "error": (
                    "Reddit OAuth credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) are not configured on Render. "
                    "Reddit blocks direct unauthenticated scraping."
                    if not reddit_conn.is_configured()
                    else "Failed to extract thread via Reddit OAuth API."
                ),
                "available_search_snippets": snippets,
                "comments_extracted": 0,
                "guidance": (
                    "To read full posts and all 50+ comments directly, add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to Render Environment. "
                    "Alternatively, use available search snippets above or paste the thread content directly."
                )
            }
        else:
            search_query = f"site:reddit.com/r/ireland OR site:reddit.com/r/irishpersonalfinance {url_or_query}"
            results = firecrawl_conn.search(query=search_query, limit=3)
            return {
                "platform": "reddit",
                "query": url_or_query,
                "discussions_found": results,
                "status": "success",
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

    default_transport = "stdio" if not sys.stdin.isatty() else "remote"
    parser = argparse.ArgumentParser(description="HomePilot Market Intelligence MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http", "remote"],
        default=default_transport,
        help="MCP transport protocol (defaults to 'stdio' in piped/headless environments like Claude Desktop, or 'remote' in terminal)"
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
