import pytest
from src.intelligence.authority_discovery import AuthoritySourceDiscoveryEngine
from src.storage.repository import IntelligenceRepository

def test_authority_discovery_identifies_gaps():
    engine = AuthoritySourceDiscoveryEngine()
    gaps = engine.identify_research_gaps()
    assert len(gaps) >= 3
    assert any("macro completions" in g.lower() for g in gaps)
    assert any("rental" in g.lower() for g in gaps)

def test_authority_discovery_discovers_and_scores_candidates():
    repo = IntelligenceRepository()
    engine = AuthoritySourceDiscoveryEngine(repository=repo)
    candidates = engine.discover_and_evaluate_candidates()
    
    assert len(candidates) >= 5
    # Verify CSO, RTB, Central Bank are present with high authority
    names = [c.name for c in candidates]
    assert any("Central Statistics Office" in n for n in names)
    assert any("Central Bank" in n for n in names)
    assert any("Residential Tenancies Board" in n for n in names)

    for c in candidates:
        assert c.authority_score >= 90.0
        assert c.review_status == "pending_approval"
        assert c.justification
        assert c.identified_gap
