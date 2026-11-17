"""Unit tests for Campaign-Driven Dynamic Batching & Out-of-Focus Regional Spike Alerting."""

import pytest
from src.storage.repository import IntelligenceRepository
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.scheduling.daemon import ProductionSchedulerDaemon
from src.mcp_server import (
    set_active_campaign_target,
    get_active_campaign_target,
    trigger_out_of_focus_regional_alert,
    get_out_of_focus_regional_alerts,
    get_latest_daily_briefing
)

def test_repository_active_campaign_focus():
    repo = IntelligenceRepository()
    updated = repo.set_active_campaign_focus(
        campaign_name="Q1 Cork & Galway Expansion",
        target_counties=["Cork", "Galway"],
        target_personas=["seg_1_frustrated_ftb"],
        notes="Expanding beyond Leinster into southern & western growth nodes."
    )
    assert updated["campaign_name"] == "Q1 Cork & Galway Expansion"
    assert updated["target_counties"] == ["Cork", "Galway"]

    fetched = repo.get_active_campaign_focus()
    assert fetched["campaign_name"] == "Q1 Cork & Galway Expansion"
    assert "Cork" in fetched["target_counties"]
    assert "Galway" in fetched["target_counties"]

def test_daily_briefing_dynamic_campaign_batching():
    repo = IntelligenceRepository()
    repo.set_active_campaign_focus(
        campaign_name="Leinster Commuter Sprint",
        target_counties=["Kildare", "Meath", "Wicklow"]
    )
    generator = DailyBriefingGenerator(repository=repo)
    briefing = generator.generate_morning_briefing()

    assert briefing.active_campaign_name == "Leinster Commuter Sprint"
    assert briefing.target_counties == ["Kildare", "Meath", "Wicklow"]
    # Check that report markdown contains sections for each targeted county
    assert "County Kildare" in briefing.markdown_report
    assert "County Meath" in briefing.markdown_report
    assert "County Wicklow" in briefing.markdown_report

def test_out_of_focus_regional_spike_alerting():
    repo = IntelligenceRepository()
    # Set campaign focus to Meath and Kildare
    repo.set_active_campaign_focus(
        campaign_name="Commuter Belt Focus",
        target_counties=["Meath", "Kildare"]
    )

    # An unexpected spike occurs in County Cork (out of focus!)
    repo.record_regional_spike_alert({
        "county": "Cork",
        "headline": "Cork City Planning Refusal Blocks 450 Units",
        "summary": "Major judicial review quashes strategic housing development in Douglas, pushing rental inflation to +11.4%.",
        "facts": ["450 units blocked", "+11.4% rent surge", "Douglas LEA"],
        "strategic_implications": "Accelerates FTB displacement into West Cork satellite towns.",
        "category": "Planning & Supply Crisis"
    })

    alerts = repo.list_regional_spike_alerts()
    assert len(alerts) >= 1
    assert alerts[0]["county"] == "Cork"

    # Now generate briefing: it must detect Cork as an out-of-focus spike!
    generator = DailyBriefingGenerator(repository=repo)
    briefing = generator.generate_morning_briefing()

    assert len(briefing.out_of_focus_regional_alerts) >= 1
    assert any(a["county"] == "Cork" for a in briefing.out_of_focus_regional_alerts)
    assert "Out-of-Focus Regional Spike Alerts" in briefing.markdown_report
    assert "County Cork — Cork City Planning Refusal Blocks 450 Units" in briefing.markdown_report
    assert "Strategic Implication for HomePilot" in briefing.markdown_report

def test_mcp_campaign_and_spike_tools():
    # 1. Set campaign target via MCP tool
    set_res = set_active_campaign_target(
        campaign_name="Midlands Commuter Push",
        target_counties=["Laois", "Offaly", "Westmeath"],
        notes="GrokBot instructed Midlands campaign focus."
    )
    assert set_res["status"] == "active_campaign_updated"
    assert set_res["target_counties"] == ["Laois", "Offaly", "Westmeath"]

    # 2. Query campaign target via MCP tool
    current = get_active_campaign_target()
    assert current["campaign_name"] == "Midlands Commuter Push"
    assert "Offaly" in current["target_counties"]

    # 3. Trigger out-of-focus alert in Donegal via MCP tool
    alert_res = trigger_out_of_focus_regional_alert(
        county="Donegal",
        headline="Defective Concrete Blocks Grant Cap Raised",
        summary="Statutory revision increases redress ceiling to €420,000.",
        facts=["Ceiling €420,000", "Ministerial Circular 14/2026"],
        strategic_implications="Direct impact on buyer liquidity and second-hand mortgageability in the North-West."
    )
    assert alert_res["status"] == "alert_triggered"
    assert alert_res["county"] == "Donegal"

    # 4. Fetch out-of-focus alerts via MCP
    active_alerts = get_out_of_focus_regional_alerts(limit=5)
    assert any(a["county"] == "Donegal" for a in active_alerts)

    # 5. Fetch daily briefing via MCP: should batch for Laois/Offaly/Westmeath and feature Donegal alert!
    mcp_briefing = get_latest_daily_briefing()
    assert "Midlands Commuter Push" in mcp_briefing["title"]
    assert "Donegal" in mcp_briefing["markdown_report"]

def test_scheduler_daemon_executes_dynamic_campaign():
    repo = IntelligenceRepository()
    repo.set_active_campaign_focus(
        campaign_name="Daemon Multi-County Verification",
        target_counties=["Kildare", "Meath"]
    )
    daemon = ProductionSchedulerDaemon(repository=repo)
    result = daemon.execute_daily_briefing_job()

    assert result["status"] == "success"
    assert result["campaign_name"] == "Daemon Multi-County Verification"
    assert result["target_counties"] == ["Kildare", "Meath"]
