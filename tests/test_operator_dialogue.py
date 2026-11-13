import pytest
from src.intelligence.operator_dialogue import OperatorDialogueEngine
from src.models.asset import GeneratedAsset, AssetPayload
from src.storage.repository import IntelligenceRepository

def test_operator_dialogue_dual_signoff_flow():
    repo = IntelligenceRepository()
    engine = OperatorDialogueEngine(repository=repo)

    # Seed an asset in pending_review
    asset_id = "asset_test_signoff_01"
    asset = GeneratedAsset(
        asset_id=asset_id,
        campaign_id="camp_test",
        asset_type="x_thread",
        content_payload=AssetPayload(
            headline="Initial Hook",
            copy_body="Initial draft text for thread.",
            evidence_citations=["evid_1", "evid_2"]
        ),
        review_status="pending_review"
    )
    repo.save_asset(asset)

    # 1. Grok revision turn
    revised = engine.revise_asset_with_grok(
        asset_id=asset_id,
        operator_instruction="Add emphasis on Central Bank exemptions",
        operator_id="lead_operator"
    )
    assert revised.review_status == "pending_review"
    assert "central bank" in revised.content_payload.copy_body.lower() or "revised by grok bot" in revised.reviewer_notes.lower()

    # 2. Sequencing guard: Operator 2 cannot approve before Operator 1
    with pytest.raises(ValueError) as exc:
        engine.signoff_operator_2(asset_id=asset_id, operator_id="legal_lead")
    assert "Sequencing Violation" in str(exc.value)

    # 3. Operator 1 approves
    op1_asset = engine.signoff_operator_1(
        asset_id=asset_id,
        operator_id="product_lead",
        notes="Verified calculation against Central Bank 4.0x rules."
    )
    assert op1_asset.review_status == "operator_1_approved"

    # 4. Operator 2 approves (Rule B-04 complete)
    op2_asset = engine.signoff_operator_2(
        asset_id=asset_id,
        operator_id="compliance_lead",
        notes="Mandatory disclaimers checked."
    )
    assert op2_asset.review_status == "approved"
    assert "product_lead + compliance_lead" in op2_asset.reviewed_by
