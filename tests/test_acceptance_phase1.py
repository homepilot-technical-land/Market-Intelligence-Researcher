import pytest
from src.pipeline.runner import MarketIntelligencePipeline
from src.intelligence.taxonomy import classify_text_category, TAXONOMY_REGISTRY
from src.models import DiscoveredURL

def test_tc01_source_registry_integrity():
    """TC-01: Ingest all sources from config/sources_registry.json."""
    pipeline = MarketIntelligencePipeline()
    loaded_count = pipeline.load_sources_from_registry("config/sources_registry.json")
    assert loaded_count >= 30, f"Expected >= 30 sources, got {loaded_count}"
    
    # Verify mandatory fields on each registered source
    sources = pipeline.repo.list_sources()
    for s in sources:
        assert s.source_id
        assert s.name
        assert s.root_url.startswith("http")
        assert s.ecosystem
        assert s.tier in [1, 2, 3, 4]
        assert s.cadence in ["hourly_12", "daily", "weekly", "on_release"]

def test_tc02_two_stage_discovery_filter():
    """TC-02: Verify Tier-1 heuristic rejection and Tier-2 semantic approval."""
    pipeline = MarketIntelligencePipeline()
    
    # Tier 1 rejects
    assert pipeline.filter_url_tier1("https://www.ccpc.ie/buying-a-car/used-cars")[0] is False
    assert pipeline.filter_url_tier1("https://www.ccpc.ie/privacy-policy")[0] is False
    assert pipeline.filter_url_tier1("https://www.ccpc.ie/cookie-settings")[0] is False
    
    # Tier 1 approves
    assert pipeline.filter_url_tier1("https://www.ccpc.ie/buying-a-home/mortgage-guide")[0] is True
    assert pipeline.filter_url_tier1("https://www.ccpc.ie/consumer-credit/financial-difficulty")[0] is True
    
    # Tier 2 semantic pre-filtering scores
    score_home = pipeline.evaluate_semantic_score("https://www.ccpc.ie/buying-a-home/mortgage-guide")
    assert score_home >= 0.6
    
    score_diff = pipeline.evaluate_semantic_score("https://www.ccpc.ie/consumer-credit/financial-difficulty")
    assert score_diff >= 0.5

def test_tc03_idempotent_storage_and_zero_duplicate_writes():
    """TC-03: Repeated processing of identical content must generate 0 duplicate writes."""
    pipeline = MarketIntelligencePipeline()
    pipeline.load_sources_from_registry("config/sources_registry.json")
    
    test_url = "https://www.ccpc.ie/buying-a-home/mortgage-guide"
    
    # First extraction
    doc1 = pipeline.process_url("ccpc_homebuyers_guides", test_url)
    assert doc1 is not None
    assert doc1.version == 1
    
    # Second extraction on identical content -> must return None (idempotent no-op)
    doc2 = pipeline.process_url("ccpc_homebuyers_guides", test_url)
    assert doc2 is None, "Expected idempotent no-op for identical content"

def test_tc04_twelve_category_classification_accuracy():
    """TC-04: Verify category classifier across gold-standard test samples."""
    test_cases = [
        ("Revenue has published updated guidelines on the Help to Buy incentive for first-time buyers.", "FTBS"),
        ("The Property Price Register recorded 1,200 residential transactions across County Dublin.", "PPTR"),
        ("The Central Bank has announced changes to macroprudential mortgage rate and loan to income limits.", "MFPL"),
        ("Glenveagh has launched 350 starter homes in a new residential development phase in Navan.", "HSRD"),
        ("Daft report shows average asking prices increased by 6.2% across Irish residential property markets.", "IRPM"),
        ("An Bord Pleanála has granted planning permission for an LRD residential scheme in Clondalkin.", "PLZN")
    ]
    
    for text, expected_code in test_cases:
        predicted = classify_text_category(text)
        assert predicted == expected_code, f"Failed for text: '{text[:40]}...'. Expected {expected_code}, got {predicted}"
