import pytest
from fastapi.testclient import TestClient
from src.api.intelligence_api import app

def test_health_endpoint():
    with TestClient(app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["service"] == "intelligence_service"
        assert "total_sources_registered" in data

def test_sources_endpoint():
    with TestClient(app) as client:
        res = client.get("/sources")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 30

def test_candidate_sources_endpoint():
    with TestClient(app) as client:
        res = client.get("/sources/candidates")
        assert res.status_code == 200
        data = res.json()
        assert data["count"] >= 5

def test_create_research_objective():
    with TestClient(app) as client:
        payload = {
            "objective_id": "obj_ftb_affordability_2026",
            "title": "Evaluate First-Time Buyer Affordability in Navan",
            "strategic_dimension": "financial_confidence",
            "core_questions": ["What is the median starter home price?", "What is the typical deposit gap?"]
        }
        res = client.post("/research/objectives", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "created"
        assert data["objective"]["objective_id"] == "obj_ftb_affordability_2026"

def test_create_research_assessment_endpoint():
    with TestClient(app) as client:
        payload = {
            "title": "Weekly Commuter Affordability Memo",
            "analysis": "Tri-weekly exploration into Kildare commuter rail corridors.",
            "key_findings": ["Naas median starter price €395k", "HTB claims take 7 weeks"],
            "buyer_pain_points": ["Prolonged approval delays"],
            "strategic_implications": ["Highlight parallel processing guide"],
            "category": "FTBS",
            "county": "Kildare",
            "confidence_score": 88.0
        }
        res = client.post("/research/assessments", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "persisted_to_mongodb"
        assert "doc_id" in data
        assert "insight_id" in data
