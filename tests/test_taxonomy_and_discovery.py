import pytest
from src.intelligence.taxonomy import DynamicTaxonomyEngine, TAXONOMY_REGISTRY
from src.intelligence.authority_discovery import AuthoritySourceDiscoveryEngine
from src.connectors.firecrawl_connector import FirecrawlConnector

def test_dynamic_taxonomy_engine_seed_keywords():
    engine = DynamicTaxonomyEngine()
    ftbs_kws = engine.get_keywords("FTBS")
    assert "help to buy" in ftbs_kws
    assert "first home scheme" in ftbs_kws

def test_dynamic_taxonomy_engine_add_keyword():
    engine = DynamicTaxonomyEngine()
    added = engine.add_dynamic_keyword("FTBS", "meath commuter ceiling")
    assert added is True
    assert "meath commuter ceiling" in engine.get_keywords("FTBS")

def test_dynamic_taxonomy_engine_extract_emergent_keywords():
    engine = DynamicTaxonomyEngine()
    sample_text = """
    Revenue announced updates to the first-time buyer scheme.
    A new commuter county price cap has been introduced for starter homes.
    Local authorities will review the shared equity subsidy thresholds.
    """
    emergent = engine.extract_emergent_keywords(sample_text, category_code="FTBS")
    assert len(emergent) > 0
    assert any("price cap" in kw or "scheme" in kw or "subsidy" in kw for kw in emergent)

def test_dynamic_taxonomy_query_generation():
    engine = DynamicTaxonomyEngine()
    queries = engine.generate_authority_discovery_queries(category_code="FTBS", county="Meath")
    assert len(queries) > 0
    assert any("site:gov.ie" in q or "site:.ie" in q for q in queries)
    assert any("Meath" in q for q in queries)

def test_authority_discovery_with_firecrawl():
    connector = FirecrawlConnector(api_key="")
    discovery = AuthoritySourceDiscoveryEngine()
    candidates = discovery.discover_sources_via_firecrawl(connector=connector, max_queries=1, county="Kildare")
    assert len(candidates) > 0
    for c in candidates:
        assert c.authority_score > 70
        assert c.review_status == "pending_approval"
