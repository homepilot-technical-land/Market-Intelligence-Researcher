from typing import Optional, Dict
from src.models.insight import ScoringBreakdown

class IntelligenceScorer:
    """Calculates the composite 0-100 Intelligence Score using the 6-dimension formula."""

    # Weights defined in the Technical Implementation Spec
    WEIGHTS = {
        "relevance": 0.25,
        "impact": 0.25,
        "confidence": 0.20,
        "time_sensitivity": 0.15,
        "campaign_alignment": 0.10,
        "geography": 0.05
    }

    @classmethod
    def calculate(
        cls,
        s_relevance: float,
        s_impact: float,
        s_confidence: float,
        s_time_sensitivity: float,
        s_campaign_alignment: float,
        s_geography: float
    ) -> ScoringBreakdown:
        """Computes the weighted composite score and returns a validated ScoringBreakdown."""
        # Clamp all sub-scores between 0.0 and 100.0
        s_rel = max(0.0, min(100.0, float(s_relevance)))
        s_imp = max(0.0, min(100.0, float(s_impact)))
        s_conf = max(0.0, min(100.0, float(s_confidence)))
        s_time = max(0.0, min(100.0, float(s_time_sensitivity)))
        s_camp = max(0.0, min(100.0, float(s_campaign_alignment)))
        s_geo = max(0.0, min(100.0, float(s_geography)))

        composite = (
            cls.WEIGHTS["relevance"] * s_rel +
            cls.WEIGHTS["impact"] * s_imp +
            cls.WEIGHTS["confidence"] * s_conf +
            cls.WEIGHTS["time_sensitivity"] * s_time +
            cls.WEIGHTS["campaign_alignment"] * s_camp +
            cls.WEIGHTS["geography"] * s_geo
        )

        return ScoringBreakdown(
            composite_score=round(composite, 2),
            s_relevance=s_rel,
            s_impact=s_imp,
            s_confidence=s_conf,
            s_time_sensitivity=s_time,
            s_campaign_alignment=s_camp,
            s_geography=s_geo
        )

    @classmethod
    def evaluate_gate(cls, composite_score: float) -> str:
        """Determines the processing action based on composite score thresholds."""
        if composite_score >= 70.0:
            return "strategic_clustering" # Full 10 Qs and campaign clustering
        elif composite_score >= 50.0:
            return "weekly_digest"       # Queue for weekly intelligence summary
        else:
            return "background_archive"   # Archive as background context
