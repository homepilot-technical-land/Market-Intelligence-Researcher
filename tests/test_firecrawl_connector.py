import pytest
from unittest.mock import MagicMock, patch
from src.connectors.firecrawl_connector import FirecrawlConnector
from src.coordination.budget_tracker import BudgetGovernanceTracker

def test_firecrawl_configuration_check():
    empty_connector = FirecrawlConnector(api_key="")
    assert not empty_connector.is_configured()

    dummy_connector = FirecrawlConnector(api_key="your_firecrawl_api_key_here")
    assert not dummy_connector.is_configured()

    configured_connector = FirecrawlConnector(api_key="fc-live-test-key-123")
    assert configured_connector.is_configured()

def test_firecrawl_interact_action_builders():
    wait_act = FirecrawlConnector.build_wait_action(2000)
    assert wait_act == {"type": "wait", "milliseconds": 2000}

    click_act = FirecrawlConnector.build_click_action("button#accept")
    assert click_act == {"type": "click", "selector": "button#accept"}

    scroll_act = FirecrawlConnector.build_scroll_action("down", 600)
    assert scroll_act == {"type": "scroll", "direction": "down", "amount": 600}

    write_act = FirecrawlConnector.build_write_action("input#county", "Kildare")
    assert write_act == {"type": "write", "selector": "input#county", "text": "Kildare"}

def test_firecrawl_domain_scoping_policy():
    connector = FirecrawlConnector(api_key="")
    
    # 1. Instagram, TikTok, and X/Twitter must be strictly excluded from Firecrawl
    assert connector.is_permitted_url("https://www.instagram.com/p/irishhomes/") is False
    assert connector.is_permitted_url("https://www.tiktok.com/@housingtips") is False
    assert connector.is_permitted_url("https://x.com/ccpc_ie/status/123456") is False
    assert connector.is_permitted_url("https://twitter.com/RevenueIE/status/789") is False

    # 2. Irish housing websites and institutional links must be permitted
    assert connector.is_permitted_url("https://www.revenue.ie/en/property/help-to-buy.aspx") is True
    assert connector.is_permitted_url("https://www.ccpc.ie/buying-a-home") is True
    assert connector.is_permitted_url("https://www.daft.ie/for-sale/dublin") is True
    assert connector.is_permitted_url("https://glenveagh.ie/developments") is True

    # 3. Facebook communities relating to HomePilot / Irish FTB are permitted
    assert connector.is_permitted_url(
        url="https://www.facebook.com/groups/firsttimebuyersireland/",
        title="First Time Buyers Ireland Discussion Group",
        description="Public peer support and mortgage guidance"
    ) is True
    assert connector.is_permitted_url(
        url="https://www.facebook.com/groups/homepilotftbcommunity/",
        title="HomePilot FTB Community",
        description="Buyer discussions"
    ) is True

    # 4. Generic non-community Facebook links without FTB context are rejected
    assert connector.is_permitted_url("https://www.facebook.com/randomuser/posts/1234") is False

def test_firecrawl_scrape_simulation_fallback():
    connector = FirecrawlConnector(api_key="")
    res = connector.scrape_url("https://www.ccpc.ie/buying-a-home")
    assert res["status"] == 200
    assert "Buying A Home" in res["title"]
    assert "Help to Buy" in res["markdown"]
    assert res["success"] is True

def test_firecrawl_search_simulation_fallback():
    connector = FirecrawlConnector(api_key="")
    results = connector.search("Irish mortgage interest relief")
    assert len(results) >= 2
    assert any("revenue.ie" in r["url"] for r in results)

def test_firecrawl_search_then_scrape_two_step():
    connector = FirecrawlConnector(api_key="")
    results = connector.search_then_scrape(
        query="Irish first home scheme",
        search_limit=5,
        scrape_limit=2,
        keyword_filters=["scheme", "home", "buyer"]
    )
    assert len(results) <= 2
    assert len(results) > 0
    for r in results:
        assert "url" in r
        assert "markdown" in r
        assert len(r["markdown"]) > 50

def test_firecrawl_facebook_community_search():
    connector = FirecrawlConnector(api_key="")
    results = connector.search_facebook_communities(query="First Time Buyers Ireland", limit=2)
    assert len(results) > 0
    for r in results:
        assert "url" in r
        assert "markdown" in r

def test_firecrawl_budget_tracker_enforcement():
    tracker = BudgetGovernanceTracker()
    initial_credits = tracker.get_current_burn().firecrawl_credits_used

    try:
        # Force exhaustion
        burn = tracker.get_current_burn()
        burn.firecrawl_credits_used = 5000
        tracker._local_burn_store[tracker._current_month()] = burn.model_dump()

        connector = FirecrawlConnector(api_key="fc-test", budget_tracker=tracker)
        res = connector.scrape_url("https://www.example.com")
        assert res["status"] == 429
        assert "Blocked by Budget Governor" in res["title"]
    finally:
        # Restore credits
        burn = tracker.get_current_burn()
        burn.firecrawl_credits_used = initial_credits
        tracker._local_burn_store[tracker._current_month()] = burn.model_dump()
        tracker._save_burn_state()

def test_firecrawl_budget_consumption_recording():
    tracker = BudgetGovernanceTracker()
    initial_credits = tracker.get_current_burn().firecrawl_credits_used

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "success": True,
        "data": {
            "markdown": "# Test Title\nContent here",
            "metadata": {"title": "Test Title", "statusCode": 200}
        }
    }
    mock_client.post.return_value = mock_resp

    connector = FirecrawlConnector(api_key="fc-live-key", budget_tracker=tracker)
    connector.client = mock_client

    res = connector.scrape_url("https://www.revenue.ie/test-page")
    assert res["status"] == 200
    assert tracker.get_current_burn().firecrawl_credits_used == initial_credits + 1
