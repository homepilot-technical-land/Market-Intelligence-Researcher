"""
Tests for Phase 5 Production Operations & Hardening.
Verifies:
1. Zero-Trust PII Scrubber (Irish phone, email, IBAN redaction).
2. RFC 7807 Standard Error Handlers in FastAPI.
3. Autonomous Production Scheduler Daemon cycle execution.
"""

import pytest
from fastapi.testclient import TestClient
from src.normalisation.pii_scrubber import PIIScrubber
from src.api.intelligence_api import app
from src.api.middleware import RFC7807Exception
from src.scheduling.daemon import ProductionSchedulerDaemon
from src.storage.repository import IntelligenceRepository
from src.pipeline.runner import MarketIntelligencePipeline

# ---------------------------------------------------------
# 1. Zero-Trust PII Scrubber Tests
# ---------------------------------------------------------

def test_pii_scrubber_redacts_irish_mobile_and_landline():
    text = (
        "Contact the buyer at 087 123 4567 or via office landline +353 (01) 234 5678. "
        "Alternative mobile: 085-987-6543."
    )
    scrubbed, stats = PIIScrubber.scrub_text(text)
    assert stats["phones"] >= 3
    assert "087 123 4567" not in scrubbed
    assert "085-987-6543" not in scrubbed
    assert "[REDACTED_PHONE]" in scrubbed

def test_pii_scrubber_redacts_personal_emails():
    text = "Please forward conveyancing contracts to john.doe@propertylawyer.ie and mary@example.com."
    scrubbed, stats = PIIScrubber.scrub_text(text)
    assert stats["emails"] == 2
    assert "john.doe@propertylawyer.ie" not in scrubbed
    assert "mary@example.com" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed

def test_pii_scrubber_redacts_iban():
    text = "Transfer the deposit to Irish account IE29 AIBK 9311 5212 3456 78 immediately."
    scrubbed, stats = PIIScrubber.scrub_text(text)
    assert stats["ibans"] >= 1
    assert "IE29 AIBK 9311 5212 3456 78" not in scrubbed
    assert "[REDACTED_IBAN]" in scrubbed

def test_pii_scrubber_clean_text_unchanged():
    text = "The median price for 3-bedroom semi-detached homes in Navan rose by 8.4% according to PPR records."
    scrubbed, stats = PIIScrubber.scrub_text(text)
    assert sum(stats.values()) == 0
    assert scrubbed == text


# ---------------------------------------------------------
# 2. RFC 7807 Problem Details Tests
# ---------------------------------------------------------

@pytest.fixture
def api_client():
    return TestClient(app)

def test_rfc7807_not_found_returns_problem_json(api_client):
    response = api_client.get("/non-existent-endpoint-404")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    
    body = response.json()
    assert body["status"] == 404
    assert body["title"] == "Not Found"
    assert "detail" in body
    assert body["type"] == "https://homepilot.ie/errors/http-404"

def test_rfc7807_validation_error_returns_problem_json(api_client):
    # Post invalid payload to trigger RequestValidationError
    response = api_client.post("/research/objectives", json={"invalid_field": 123})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    
    body = response.json()
    assert body["status"] == 422
    assert body["title"] == "Request Validation Failed"
    assert "invalidParams" in body
    assert len(body["invalidParams"]) > 0
    assert body["type"] == "https://homepilot.ie/errors/validation-failed"


# ---------------------------------------------------------
# 3. Production Scheduler Daemon Tests
# ---------------------------------------------------------

def test_scheduler_daemon_single_cycle_execution():
    repo = IntelligenceRepository()
    pipeline = MarketIntelligencePipeline(repository=repo)
    daemon = ProductionSchedulerDaemon(repository=repo, pipeline=pipeline)

    # Execute single cycle with max_sources=1 for swift execution
    cycle_result = daemon.run_all_cycle_once(max_sources=1)

    assert cycle_result["daemon_healthy"] is True
    assert cycle_result["briefing_job"]["status"] == "success"
    assert "briefing_id" in cycle_result["briefing_job"]
    assert cycle_result["cadence_job"]["status"] == "success"
    assert cycle_result["cadence_job"]["sources_checked"] <= 1
    assert cycle_result["gap_batch_job"]["status"] == "success"
