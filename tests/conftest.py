import os
import pytest
from src.storage.mongo_client import MongoDBManager

# Force tests to use an isolated test database
os.environ["MONGODB_DB_NAME"] = "homepilot_intelligence_test"

@pytest.fixture(autouse=True)
def clean_test_database():
    """Ensures test database is cleaned before and after tests for complete hermetic isolation."""
    manager = MongoDBManager(db_name="homepilot_intelligence_test")
    if manager.connect():
        # Drop test database so tests start with a clean slate
        manager.client.drop_database("homepilot_intelligence_test")
    yield
    if manager.connect():
        manager.client.drop_database("homepilot_intelligence_test")
