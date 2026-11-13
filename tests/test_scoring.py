import pytest
from src.intelligence.scoring import IntelligenceScorer

def test_scoring_weights_sum_to_one():
    total_weight = sum(IntelligenceScorer.WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6, f"Weights must sum to 1.0, got {total_weight}"

def test_composite_score_calculation():
    score = IntelligenceScorer.calculate(
        s_relevance=100.0,
        s_impact=80.0,
        s_confidence=90.0,
        s_time_sensitivity=70.0,
        s_campaign_alignment=60.0,
        s_geography=80.0
    )
    # 0.25*100 + 0.25*80 + 0.20*90 + 0.15*70 + 0.10*60 + 0.05*80
    # = 25 + 20 + 18 + 10.5 + 6 + 4 = 83.5
    assert score.composite_score == 83.5
    assert IntelligenceScorer.evaluate_gate(score.composite_score) == "strategic_clustering"

def test_gate_thresholds():
    assert IntelligenceScorer.evaluate_gate(75.0) == "strategic_clustering"
    assert IntelligenceScorer.evaluate_gate(62.0) == "weekly_digest"
    assert IntelligenceScorer.evaluate_gate(35.0) == "background_archive"
