import pytest
from src.intelligence.persona_engine import DynamicPersonaEngine
from src.models.document import ExtractedDocument
from src.storage.repository import IntelligenceRepository

def test_dynamic_persona_engine_bootstrap_and_discovery():
    repo = IntelligenceRepository()
    engine = DynamicPersonaEngine(repository=repo)
    
    # Verify bootstrap seeded the defaults
    personas = repo.list_personas()
    assert len(personas) >= 5
    ids = [p.segment_id for p in personas]
    assert "seg_1_frustrated_ftb" in ids
    assert "seg_2_mortgage_ready_optimiser" in ids

    # Check 3 R's Duty Allocation on default persona
    p1 = repo.get_persona("seg_1_frustrated_ftb")
    assert p1 is not None
    assert p1.journey_mapping.duty_allocation.requires_human_validation is True
    assert "Bot" in p1.journey_mapping.duty_allocation.role
    assert "Review Queue" in p1.journey_mapping.duty_allocation.route

    # Test feed evaluation for new dynamic persona: Commuter Straddler
    sample_doc = ExtractedDocument.create(
        source_id="glenveagh_developments",
        url="https://glenveagh.ie/developments/navan-meath",
        markdown="New residential phase launched in Navan, Co. Meath with 250 starter homes. Prices test regional First Home Scheme price cap limits for Meath buyers.",
        title="Glenveagh Navan Launch"
    )
    
    discovered = engine.evaluate_feed_for_persona_discovery(sample_doc)
    assert discovered is not None
    assert discovered.segment_id == "dyn_seg_commuter_cap_straddler"
    assert discovered.origin == "discovered_feed"
    assert "Commuter Belt" in str(discovered.demographics)
    assert discovered.influences_on_perceptions.brand_image != ""
    assert discovered.journey_mapping.primary_stage == "Regional Search & Bidding"
    assert len(discovered.evidence_citations) > 0
    
    # Check 3 R's Duty Allocation on dynamic persona
    assert discovered.journey_mapping.duty_allocation.requires_human_validation is True
    assert "Firecrawl" in discovered.journey_mapping.duty_allocation.role
    assert "Human Operator" in discovered.journey_mapping.duty_allocation.role

    # Test feed evaluation for second dynamic persona: Grant Stacker
    grant_doc = ExtractedDocument.create(
        source_id="gov_housing",
        url="https://www.gov.ie/en/publication/vacant-property-refurbishment-grant/",
        markdown="Department of Housing updates guidelines on the Vacant Property Refurbishment Grant under Croí Cónaithe, offering up to €70,000 for derelict homes.",
        title="Vacant Property Refurbishment Grant Guidelines"
    )
    
    discovered_grant = engine.evaluate_feed_for_persona_discovery(grant_doc)
    assert discovered_grant is not None
    assert discovered_grant.segment_id == "dyn_seg_grant_stacker"
    assert "Croí Cónaithe" in discovered_grant.evidence_citations[0]
    assert discovered_grant.journey_mapping.duty_allocation.requires_human_validation is True

    # Verify total personas increased
    all_personas = repo.list_personas()
    assert len(all_personas) >= 7
