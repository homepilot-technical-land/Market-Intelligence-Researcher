import pytest
from src.intelligence.grok_service import GrokService, GrokResponse

def test_grok_service_fallback_and_token_accounting():
    service = GrokService()
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
