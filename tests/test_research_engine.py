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

def test_benchmark_feed_against_personas():
    from src.models.insight import MarketInsight, ScoringBreakdown
    from datetime import datetime, timezone

    repo = IntelligenceRepository()
    engine = ObjectiveResearchEngine(repository=repo)

    insight = MarketInsight(
        insight_id="ins_test_benchmark",
        doc_id="doc_test_123",
        primary_category="affordability_schemes",
        scoring=ScoringBreakdown(
            s_relevance=90,
            s_impact=88,
            s_confidence=90,
            s_time_sensitivity=80,
            s_campaign_alignment=85,
            s_geography=70,
            composite_score=88.5
        ),
        created_at=datetime.now(timezone.utc)
    )

    bench = engine.benchmark_feed_against_personas(
        insight, 
        dynamic_personas=[{"segment_id": "dyn_seg_commuter_cap_straddler", "name": "Commuter Cap Straddler"}]
    )

    assert bench["category"] == "affordability_schemes"
    assert len(bench["benchmarks"]) >= 5
    # Check 3 R's allocation
    first_bench = bench["benchmarks"][0]
    assert "three_rs_duty_allocation" in first_bench
    assert "role_bot" in first_bench["three_rs_duty_allocation"]
    assert "role_human" in first_bench["three_rs_duty_allocation"]

