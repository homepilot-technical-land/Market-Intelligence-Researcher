import os
import json
import pytest
from src.pipeline.runner import MarketIntelligencePipeline

def test_source_registry_file_exists():
    path = "config/sources_registry.json"
    assert os.path.exists(path), f"Registry missing at {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "sources" in data
    assert len(data["sources"]) >= 30, f"Expected at least 30 sources, got {len(data['sources'])}"

def test_pipeline_loads_all_sources():
    pipeline = MarketIntelligencePipeline()
    loaded_count = pipeline.load_sources_from_registry("config/sources_registry.json")
    assert loaded_count >= 30
    sources = pipeline.repo.list_sources()
    assert len(sources) == loaded_count
