import pytest
from src.coordination.budget_tracker import BudgetGovernanceTracker

def test_budget_governance_limits_and_consumption():
    tracker = BudgetGovernanceTracker()
    burn = tracker.get_current_burn()

    assert burn.firecrawl_credit_limit == 5000
    assert burn.xai_budget_limit_usd == 27.0
    assert burn.firecrawl_credits_used == 0

    # 1. Test normal Firecrawl consumption
    can_crawl, msg = tracker.can_consume_firecrawl(credits=10)
    assert can_crawl is True
    tracker.record_firecrawl_consumption(credits=10, endpoint="scrape", source_id="ccpc_guides")
    
    updated_burn = tracker.get_current_burn()
    assert updated_burn.firecrawl_credits_used == 10

    # 2. Test normal xAI consumption
    can_ai, msg = tracker.can_consume_xai(estimated_cost_usd=0.007)
    assert can_ai is True
    tracker.record_xai_consumption(cost_usd=0.007, tokens_used=1900, doc_id="doc_123")

    updated_burn = tracker.get_current_burn()
    assert updated_burn.xai_cost_usd == 0.007

    # 3. Test caching savings calculation
    tracker.record_cache_bypass(pages=100)
    updated_burn = tracker.get_current_burn()
    assert updated_burn.pages_processed_free_hash == 100
    assert updated_burn.estimated_dollars_saved_by_cache == 0.70

def test_budget_hard_stop_guards():
    tracker = BudgetGovernanceTracker()
    
    # Simulate high xAI burn exceeding $27
    tracker.record_xai_consumption(cost_usd=27.50, tokens_used=1000000, doc_id="doc_heavy")
    can_ai, msg = tracker.can_consume_xai(estimated_cost_usd=0.01)
    assert can_ai is False
    assert "monthly budget reached" in msg

    # Simulate Firecrawl exceeding 5000 credits
    tracker.record_firecrawl_consumption(credits=5005, endpoint="crawl", source_id="bulk_crawl")
    can_crawl, msg = tracker.can_consume_firecrawl(credits=1)
    assert can_crawl is False
    assert "quota exhausted" in msg
