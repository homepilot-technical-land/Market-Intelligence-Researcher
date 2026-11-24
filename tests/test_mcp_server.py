"""Unit tests for the HomePilot Market Intelligence MCP Server."""

import pytest
from src.mcp_server import (
    get_county_market_benchmarks,
    get_latest_daily_briefing,
    search_evidence_pool,
    submit_knowledge_gap,
    submit_campaign_blueprint,
    submit_research_assessment,
    ask_research_engine,
    scrape_web_url,
    search_web_sources,
    extract_social_thread,
    synthesize_x_discourse,
    repo
)

def test_mcp_get_county_market_benchmarks():
    data = get_county_market_benchmarks("Meath")
    assert data["county"] == "Meath"
    assert "ppr_affordability_benchmarks" in data
    assert "cso_housing_indicators" in data

def test_mcp_get_latest_daily_briefing():
    data = get_latest_daily_briefing("Meath")
    assert "briefing_id" in data
    assert "briefing_date" in data
    assert "macro_indicators" in data
    assert "markdown_report" in data

def test_mcp_search_evidence_pool():
    results = search_evidence_pool("First Home Scheme", limit=3)
    assert isinstance(results, list)

def test_mcp_submit_knowledge_gap():
    res = submit_knowledge_gap(
        topic="Navan Phase 4 Developer Deposit Refundability",
        questions=["What are the exact statutory terms for booking deposit forfeit?"]
    )
    assert res["status"] == "queued_for_crawler"
    assert "objective_id" in res

    # Verify stored in repository
    obj = repo.get_research_objective(res["objective_id"])
    assert obj is not None
    assert obj.title == "Navan Phase 4 Developer Deposit Refundability"

def test_mcp_submit_campaign_blueprint_rule_b02_violation():
    res = submit_campaign_blueprint(
        title="Flawed Blueprint",
        format="x_thread",
        headline="No Citations Test",
        copy_body="Some copy here...",
        citations=["ONLY_ONE_CITATION"]
    )
    assert res["status"] == "rejected_by_rule_b02"
    assert "Rule B-02 Violation" in res["error"]

def test_mcp_submit_campaign_blueprint_valid():
    res = submit_campaign_blueprint(
        title="Valid Double-Cited Blueprint",
        format="x_thread",
        headline="Why Navan starter homes exceed the cap",
        copy_body="Empirical breakdown of the €25k cliff-edge in Navan...",
        citations=["EVID-PPR-MEATH-2026", "EVID-CSO-HPM05"]
    )
    assert res["status"] == "submitted_for_operator_review"
    assert res["review_status"] == "pending_review"
    assert "asset_id" in res

def test_mcp_ask_research_engine():
    res = ask_research_engine(
        question="What is the real starter price gap in Meath?",
        county="Meath"
    )
    assert res["county"] == "Meath"
    assert "verified_market_context" in res
    assert "engine_guidance" in res

def test_mcp_scrape_web_url():
    res = scrape_web_url("https://www.revenue.ie/en/property/help-to-buy.aspx")
    assert "url" in res
    assert "markdown_content" in res
    assert "status" in res

def test_mcp_search_web_sources():
    res = search_web_sources("Meath commuter new homes", limit=2)
    assert res["query"] == "Meath commuter new homes"
    assert "results" in res
    assert "results_count" in res

def test_mcp_extract_social_thread_reddit():
    res = extract_social_thread("reddit", "First time buyer advice Navan")
    assert res["platform"] == "reddit"
    assert "discussions_found" in res

def test_mcp_extract_social_thread_reddit_url_blocked_anti_bot():
    url = "https://www.reddit.com/r/irishpersonalfinance/comments/1xwxv80/savings_journey/"
    res = extract_social_thread("reddit", url)
    assert res["platform"] == "reddit"
    assert res["status"] in ("credentials_required", "blocked_by_anti_bot")
    assert "error" in res
    assert "Help to Buy" not in res.get("content", "")

def test_mcp_scrape_reddit_returns_explicit_error_not_fake_placeholder():
    url = "https://www.reddit.com/r/irishpersonalfinance/comments/1xwxv80/savings_journey/"
    res = scrape_web_url(url)
    assert res["status"] == "error"
    assert res["http_status"] in (403, 502)
    assert "Help to Buy" not in res.get("markdown_content", "")

def test_mcp_extract_social_thread_x():
    res = extract_social_thread("x", "Central Bank mortgage caps")
    assert res["platform"] == "x"
    assert "analysis" in res
    assert "buyer_pain_points" in res

def test_mcp_extract_social_thread_facebook():
    res = extract_social_thread("facebook", "Irish Property Movers")
    assert res["platform"] == "facebook"
    assert "community_discussions" in res

def test_mcp_extract_social_thread_instagram():
    res = extract_social_thread("instagram", "Irish property interior")
    assert res["platform"] == "instagram"
    assert "results" in res

def test_mcp_synthesize_x_discourse_second_time_buyer():
    res = synthesize_x_discourse(
        topic="Selling while buying chain sales",
        county="Kildare",
        buyer_type="second_time_buyer"
    )
    assert "analysis" in res
    assert "buyer_pain_points" in res
    assert "proposed_bot_communications" in res

def test_mcp_submit_research_assessment():
    res = submit_research_assessment(
        title="Navan Commuter Cap Spread Analysis",
        analysis="Deep research assessment showing second-phase new builds priced at €385k vs €375k First Home Scheme cap.",
        key_findings=["€10,000 cap breach", "60% buyer attrition in Navan LEA"],
        buyer_pain_points=["Inability to qualify for First Home Scheme equity support"],
        strategic_implications=["Deploy HomePilot Navan Scheme Gap Simulator"],
        category="FTBS",
        county="Meath",
        confidence_score=92.0
    )
    assert res["status"] == "persisted_to_mongodb"
    assert "doc_id" in res
    assert "insight_id" in res
    assert "evidence_id" in res
    assert res["composite_score"] == 92.0

    # Verify presence in repository
    insight = repo.get_insight(res["insight_id"])
    assert insight is not None
    assert insight.primary_category == "FTBS"

