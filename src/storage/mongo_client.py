import os
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class MongoDBManager:
    """Manages MongoDB connections, collection indexes, and schema enforcement for all 14 collections."""
    
    COLLECTIONS = [
        "sources",
        "source_candidates",
        "discovered_urls",
        "documents",
        "document_versions",
        "change_events",
        "research_objectives",
        "research_runs",
        "intelligence_findings",
        "evidence_records",
        "campaign_opportunities",
        "content_assets",
        "agent_runs",
        "audience_personas"
    ]

    def __init__(self, uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB_NAME", "homepilot_intelligence")
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None

    def connect(self) -> bool:
        """Connect to MongoDB with a short timeout to fail fast if offline."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB database: {self.db_name}")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB offline at {self.uri}. Operating with memory fallback.")
            self.client = None
            self.db = None
            return False

    def is_connected(self) -> bool:
        return self.db is not None

    def initialize_indexes(self):
        """Creates indexes across all 14 core collections."""
        if not self.is_connected():
            return

        # 1. sources
        self.db.sources.create_index([("source_id", ASCENDING)], unique=True)
        self.db.sources.create_index([("active", ASCENDING), ("cadence", ASCENDING)])

        # 2. source_candidates
        self.db.source_candidates.create_index([("candidate_id", ASCENDING)], unique=True)
        self.db.source_candidates.create_index([("review_status", ASCENDING)])

        # 3. discovered_urls
        self.db.discovered_urls.create_index([("url_hash", ASCENDING)], unique=True)
        self.db.discovered_urls.create_index([("source_id", ASCENDING), ("ingestion_status", ASCENDING)])
        self.db.discovered_urls.create_index([("semantic_score", DESCENDING)])

        # 4. documents
        self.db.documents.create_index([("doc_id", ASCENDING)], unique=True)
        self.db.documents.create_index([("url", ASCENDING), ("version", DESCENDING)])
        self.db.documents.create_index([("content_hash", ASCENDING)])

        # 5. document_versions
        self.db.document_versions.create_index([("version_id", ASCENDING)], unique=True)
        self.db.document_versions.create_index([("doc_id", ASCENDING), ("version", DESCENDING)])

        # 6. change_events
        self.db.change_events.create_index([("change_id", ASCENDING)], unique=True)
        self.db.change_events.create_index([("doc_id", ASCENDING), ("detected_at", DESCENDING)])

        # 7. research_objectives
        self.db.research_objectives.create_index([("objective_id", ASCENDING)], unique=True)
        self.db.research_objectives.create_index([("active", ASCENDING)])

        # 8. research_runs
        self.db.research_runs.create_index([("run_id", ASCENDING)], unique=True)
        self.db.research_runs.create_index([("objective_id", ASCENDING)])

        # 9. intelligence_findings
        self.db.intelligence_findings.create_index([("insight_id", ASCENDING)], unique=True)
        self.db.intelligence_findings.create_index([("scoring.composite_score", DESCENDING)])
        self.db.intelligence_findings.create_index([("primary_category", ASCENDING)])

        # 10. evidence_records
        self.db.evidence_records.create_index([("evidence_id", ASCENDING)], unique=True)
        self.db.evidence_records.create_index([("doc_id", ASCENDING)])

        # 11. campaign_opportunities
        self.db.campaign_opportunities.create_index([("campaign_id", ASCENDING)], unique=True)
        self.db.campaign_opportunities.create_index([("status", ASCENDING)])

        # 12. content_assets
        self.db.content_assets.create_index([("asset_id", ASCENDING)], unique=True)
        self.db.content_assets.create_index([("campaign_id", ASCENDING)])
        self.db.content_assets.create_index([("review_status", ASCENDING)])

        # 13. agent_runs
        self.db.agent_runs.create_index([("run_id", ASCENDING)], unique=True)
        self.db.agent_runs.create_index([("agent_type", ASCENDING), ("created_at", DESCENDING)])

        # 14. audience_personas
        self.db.audience_personas.create_index([("segment_id", ASCENDING)], unique=True)
        self.db.audience_personas.create_index([("active", ASCENDING)])
        self.db.audience_personas.create_index([("origin", ASCENDING)])

        logger.info("Indexes initialized across all 14 MongoDB collections.")
