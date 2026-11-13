import pytest
from src.generators.asset_blueprint import CampaignAssetBlueprintGenerator, EvidenceDeficiencyError
from src.intelligence.theme_clustering import StrategicTheme
from src.storage.repository import IntelligenceRepository

def test_asset_blueprint_generates_all_four_formats():
    repo = IntelligenceRepository()
    gen = CampaignAssetBlueprintGenerator(repository=repo)

    theme = StrategicTheme(
        theme_id="theme_test_meath",
        title="The Commuter Equity Squeeze: County Meath",
        geographic_scope="Meath",
        strategic_dimension="financial_confidence",
        core_problem="Median prices of €410k exceed the €375k cap by €35k.",
        homepilot_positioning_hook="Simulate true purchasing power in 60s.",
        primary_tool="Scenario Simulator",
        evidence_ids=["evid_ppr_meath_01", "evid_cso_hpm05_02"],
        signals_count=2,
        severity_score=85.0
    )

    assets = gen.generate_blueprint_suite(theme)
    assert len(assets) == 4

    types = {a.asset_type for a in assets}
    assert types == {"x_thread", "instagram_carousel", "short_form_video_script", "strategic_brief"}

    for a in assets:
        assert a.review_status == "pending_review"
        assert len(a.content_payload.evidence_citations) >= 2
        assert a.campaign_id == "camp_theme_test_meath"

def test_asset_blueprint_enforces_rule_b02_double_citation():
    repo = IntelligenceRepository()
    gen = CampaignAssetBlueprintGenerator(repository=repo)

    # Flawed theme with only 1 citation
    flawed_theme = StrategicTheme(
        theme_id="theme_flawed",
        title="Unverified Narrative",
        geographic_scope="National",
        strategic_dimension="financial_confidence",
        core_problem="Some claim without sufficient citations.",
        homepilot_positioning_hook="Hook",
        primary_tool="Tool",
        evidence_ids=["only_one_evidence_id"],
        signals_count=1,
        severity_score=50.0
    )

    with pytest.raises(EvidenceDeficiencyError) as exc_info:
        gen.generate_blueprint_suite(flawed_theme)
    
    assert "Rule B-02 Violation" in str(exc_info.value)
