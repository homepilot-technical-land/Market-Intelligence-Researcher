"""Unit tests for the HomePilot Market Intelligence MCP Server."""

import pytest
from src.mcp_server import (
    get_county_market_benchmarks,
    get_latest_daily_briefing,
    search_evidence_pool,
    submit_knowledge_gap,
    submit_campaign_blueprint,
    ask_research_engine,
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
