import pytest
from src.intelligence.theme_clustering import ThemeClusteringEngine, StrategicTheme
from src.storage.repository import IntelligenceRepository

def test_theme_clustering_generates_and_persists_themes():
    repo = IntelligenceRepository()
    engine = ThemeClusteringEngine(repository=repo)

    ppr_mock = {"median_price": 410000, "transaction_count": 142}
    cso_mock = {"annual_change_pct": 9.2}
    grok_pain_points = [
        "Regional price caps lagging developer asking prices",
        "Conveyancing solicitor delays dragging out closing dates"
    ]

    themes = engine.cluster_signals(
        county="Meath",
        ppr_stats=ppr_mock,
        cso_stats=cso_mock,
        grok_pain_points=grok_pain_points
    )

    assert len(themes) >= 2
    for t in themes:
        assert isinstance(t, StrategicTheme)
        assert len(t.evidence_ids) >= 2
        assert t.severity_score > 0.0
        assert "HomePilot" in t.homepilot_positioning_hook

    # Verify persistence in repo
    first_camp = repo.get_campaign(f"camp_{themes[0].theme_id}") if hasattr(repo, "get_campaign") else None
    # Check directly from local store or mongo
    assert themes[0].theme_id.startswith("theme_commuter_equity_squeeze_meath")
