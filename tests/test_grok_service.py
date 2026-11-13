import pytest
from src.intelligence.grok_service import GrokService, GrokResponse
from src.coordination.budget_tracker import BudgetGovernanceTracker

def test_grok_service_configuration_check():
    empty_service = GrokService(api_key="")
    assert not empty_service.is_configured()

    dummy_service = GrokService(api_key="your_xai_api_key_here")
    assert not dummy_service.is_configured()

    configured_service = GrokService(api_key="xai-live-test-1234")
    assert configured_service.is_configured()

def test_grok_service_fallback_and_token_accounting():
    service = GrokService(api_key="")
    res = service.evaluate_strategic_implications(
        context_title="Revenue Help to Buy Extension",
        text_content="Revenue has updated the claim threshold for first-time buyers purchasing new builds.",
        evidence_quote="Maximum relief remains €30,000."
    )
    
    assert isinstance(res, GrokResponse)
    assert len(res.key_findings) > 0
    assert len(res.strategic_implications) > 0
    assert res.prompt_tokens > 0
    assert res.completion_tokens > 0
    assert res.cost_usd > 0.0

def test_grok_service_x_sentiment_analysis_fallback():
    service = GrokService(api_key="")
    res = service.analyze_x_platform_sentiment(topic="Irish housing first time buyers")
    assert isinstance(res, GrokResponse)
    assert "Simulated X Platform Sentiment" in res.analysis
    assert len(res.key_findings) > 0
    assert len(res.strategic_implications) > 0
    assert res.cost_usd > 0.0

def test_grok_service_budget_guard_blocks_overage():
    tracker = BudgetGovernanceTracker()
    current_burn = tracker.get_current_burn()
    orig_spend = current_burn.xai_cost_usd

    try:
        # Force exhaustion in memory
        current_burn.xai_cost_usd = 28.0
        tracker._local_burn_store[tracker._current_month()] = current_burn.model_dump()

        service = GrokService(api_key="xai-test", budget_tracker=tracker)
        res = service.evaluate_strategic_implications(
            context_title="Test Document",
            text_content="Test text",
            evidence_quote="Test quote"
        )
        assert "blocked" in res.analysis.lower()
        assert res.cost_usd == 0.0
    finally:
        # Restore actual spend
        current_burn.xai_cost_usd = orig_spend
        tracker._local_burn_store[tracker._current_month()] = current_burn.model_dump()
        tracker._save_burn_state()
