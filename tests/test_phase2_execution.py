import pytest
from src.pipeline.monitor import FeedMonitoringPipeline
from src.storage.repository import IntelligenceRepository
from src.models.document import ExtractedDocument

def test_phase2_monitoring_cycle_and_3rs_validation():
    repo = IntelligenceRepository()
    monitor = FeedMonitoringPipeline(repository=repo)
    
    # Load sources
    from src.pipeline.runner import MarketIntelligencePipeline
    p = MarketIntelligencePipeline(repository=repo)
    p.load_sources_from_registry()

    # Execute monitor cycle on targeted source
    results = monitor.execute_scheduled_monitor_cycle(source_ids=["ccpc_homebuyers_guides"])
    
    assert results["sources_checked"] == 1
    assert results["documents_processed"] > 0
    assert results["insights_generated"] > 0

    # Verify that insights have 3 R's human validation gates enabled
    personas = repo.list_personas()
    assert len(personas) >= 5
    for persona in personas:
        duty = persona.journey_mapping.duty_allocation
        assert duty.role != ""
        assert duty.rule != ""
        assert duty.route != ""
        assert duty.requires_human_validation is True

    # Re-running on identical content must trigger idempotent no-ops (0 LLM token cost)
    repeat_results = monitor.execute_scheduled_monitor_cycle(source_ids=["ccpc_homebuyers_guides"])
    assert repeat_results["idempotent_no_ops"] > 0
