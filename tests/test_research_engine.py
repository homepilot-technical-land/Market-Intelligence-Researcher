import pytest
from src.intelligence.research_engine import ObjectiveResearchEngine
from src.models.research import ResearchObjective
from src.storage.repository import IntelligenceRepository

def test_objective_research_engine_execution():
    repo = IntelligenceRepository()
    engine = ObjectiveResearchEngine(repository=repo)
    
    objective = ResearchObjective(
        objective_id="obj_ftb_financial_readiness",
        title="Understand the Financial Readiness and Hidden Cost Barriers for Irish First-Time Buyers",
        strategic_dimension="financial_confidence",
        core_questions=[
            "What are the biggest financial barriers beyond the 10% deposit?",
            "How do rising starter home prices in commuter counties impact cash buffers?",
            "What expenses do buyers underestimate between Sale Agreed and Closing?"
        ],
        target_audiences=["seg_1_frustrated_ftb", "seg_3_homeownership_planner"]
    )
    
    run = engine.execute_research_run(objective)
    
    assert run.run_id.startswith("run_obj_ftb_financial_readiness")
    assert run.status == "completed"
    assert len(run.identified_gaps) >= 2
    assert "The Frustrated First-Time Buyer" in run.consolidated_report_markdown
    assert "The Hidden Closing Cost Bottleneck" in run.consolidated_report_markdown
    assert "Total Acquisition Cost Buffer Planner" in run.consolidated_report_markdown
