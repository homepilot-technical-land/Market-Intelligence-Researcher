import pytest
from datetime import datetime, timezone
from src.observability.posthog_client import PostHogTelemetry
from src.intelligence.bilateral_bridge import BilateralCommunicationBridge, FilterFunnelResult, OperatorReviewTask
from src.models.source import IntelligenceSource
from src.models.document import ExtractedDocument
from src.storage.repository import IntelligenceRepository

def test_posthog_telemetry_event_capture():
    telemetry = PostHogTelemetry()
    # Test valid operational event
    success = telemetry.capture("document.relevance.scored", {
        "doc_id": "doc_test_101",
        "composite_score": 88.5,
        "category": "affordability_schemes"
    })
    assert success is True

    # Test invalid event rejection
    invalid = telemetry.capture("unregistered.random.event", {"data": 123})
    assert invalid is False

def test_bilateral_funnel_filtering():
    bridge = BilateralCommunicationBridge()
    source = IntelligenceSource(
        source_id="src_funnel_test",
        name="CCPC Buying Guides",
        tier=1,
        ecosystem="consumer_protection_and_market_oversight",
        root_url="https://www.ccpc.ie"
    )

    # 10 test URLs: 4 irrelevant, 3 high priority, 3 lightweight
    urls = [
        "https://www.ccpc.ie/careers/job1",
        "https://www.ccpc.ie/privacy-policy",
        "https://www.ccpc.ie/terms-and-conditions",
        "https://www.ccpc.ie/cookie-notice",
        "https://www.ccpc.ie/housing/buying-a-home",
        "https://www.ccpc.ie/mortgage/rates-calculator",
        "https://www.ccpc.ie/first-time-buyer/schemes",
        "https://www.ccpc.ie/general/about-us",
        "https://www.ccpc.ie/news/annual-speech",
        "https://www.ccpc.ie/events/webinar"
    ]

    res = bridge.process_url_funnel(urls, source)
    assert res.total_discovered == 10
    assert res.irrelevant_discarded == 4
    assert res.high_priority_grok_dispatched == 3
    assert res.light_processed == 3
    assert res.estimated_tokens_saved > 0

def test_bilateral_grok_dialogue_and_operator_gate():
    repo = IntelligenceRepository()
    bridge = BilateralCommunicationBridge(repository=repo)
    source = IntelligenceSource(
        source_id="src_statutory_test",
        name="Gov.ie Housing Policy",
        tier=1,
        ecosystem="statutory_policy_and_legislation",
        root_url="https://www.gov.ie"
    )

    doc = ExtractedDocument.create(
        source_id=source.source_id,
        url="https://www.gov.ie/en/publication/first-home-scheme-caps",
        markdown="# First Home Scheme Price Ceilings\nLocal Authority price caps for Meath have been revised to €375,000 for newly constructed homes.",
        title="First Home Scheme Price Ceilings Revised"
    )

    # 1. Tier 1: Internal assessment
    insight = bridge.synthesize_internal_assessment(doc, source)
    assert insight.primary_category in ["FTBS", "SPLC", "MFPL", "affordability_schemes", "first_time_buyer_homes", "statutory_policy"]
    assert insight.scoring.composite_score > 0

    # 2. Tier 2 & Tier 3: Bilateral Grok dialogue and operator validation gate
    insight, review_task = bridge.bilateral_grok_dialogue(insight, doc)
    assert insight.ten_questions is not None
    assert insight.ten_questions.iceberg is not None
    assert review_task is not None
    assert review_task.status == "pending"

    # 3. Tier 3 Human Operator Feedback Loop
    approved_insight = bridge.apply_human_operator_feedback(
        review_task,
        feedback="Verified against Housing Agency statutory circular. Approved for persona evolution.",
        approved=True
    )
    assert approved_insight.status == "clustered"
    assert approved_insight.scoring.s_confidence == 95.0
