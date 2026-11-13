import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.storage.mongo_client import MongoDBManager
from src.models import (
    IntelligenceSource,
    SourceCandidate,
    DiscoveredURL,
    ExtractedDocument,
    ContentChange,
    SourceEvidence,
    MarketInsight,
    ResearchObjective,
    ResearchRun,
    CampaignOpportunity,
    GeneratedAsset,
    AgentRun,
    AudiencePersona
)

logger = logging.getLogger(__name__)

class IntelligenceRepository:
    """Unified repository supporting all 14 production collections across MongoDB and memory fallback."""

    def __init__(self, db_manager: Optional[MongoDBManager] = None):
        self.db_manager = db_manager or MongoDBManager()
        self._connected = self.db_manager.connect()
        if self._connected:
            self.db_manager.initialize_indexes()

        self._store: Dict[str, Dict[str, Any]] = {
            c: {} for c in MongoDBManager.COLLECTIONS
        }

    # --- 1. sources ---
    def upsert_source(self, source: IntelligenceSource) -> bool:
        data = source.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.sources.update_one({"source_id": source.source_id}, {"$set": data}, upsert=True)
        self._store["sources"][source.source_id] = data
        return True

    def get_source(self, source_id: str) -> Optional[IntelligenceSource]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.sources.find_one({"source_id": source_id})
            if doc:
                doc.pop("_id", None)
                return IntelligenceSource(**doc)
        data = self._store["sources"].get(source_id)
        return IntelligenceSource(**data) if data else None

    def list_sources(self, active_only: bool = True) -> List[IntelligenceSource]:
        if self._connected and self.db_manager.db is not None:
            query = {"active": True} if active_only else {}
            cursor = self.db_manager.db.sources.find(query)
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(IntelligenceSource(**doc))
            return results
        return [IntelligenceSource(**v) for v in self._store["sources"].values() if not active_only or v.get("active", True)]

    # --- 2. source_candidates ---
    def add_candidate_source(self, candidate: SourceCandidate) -> bool:
        data = candidate.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.source_candidates.update_one({"candidate_id": candidate.candidate_id}, {"$set": data}, upsert=True)
        self._store["source_candidates"][candidate.candidate_id] = data
        return True

    def list_candidate_sources(self, status: str = "pending_approval") -> List[SourceCandidate]:
        if self._connected and self.db_manager.db is not None:
            cursor = self.db_manager.db.source_candidates.find({"review_status": status})
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(SourceCandidate(**doc))
            return results
        return [SourceCandidate(**v) for v in self._store["source_candidates"].values() if v.get("review_status") == status]

    # --- 3. discovered_urls ---
    def upsert_url(self, url_item: DiscoveredURL) -> bool:
        data = url_item.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.discovered_urls.update_one({"url_hash": url_item.url_hash}, {"$set": data}, upsert=True)
        self._store["discovered_urls"][url_item.url_hash] = data
        return True

    # --- 4 & 5. documents & document_versions ---
    def save_document(self, doc: ExtractedDocument) -> bool:
        data = doc.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.documents.update_one({"doc_id": doc.doc_id}, {"$set": data}, upsert=True)
            version_record = {
                "version_id": f"{doc.doc_id}_v{doc.version}",
                "doc_id": doc.doc_id,
                "version": doc.version,
                "content_hash": doc.content_hash,
                "markdown": doc.markdown,
                "recorded_at": datetime.utcnow()
            }
            self.db_manager.db.document_versions.update_one({"version_id": version_record["version_id"]}, {"$set": version_record}, upsert=True)
        self._store["documents"][doc.doc_id] = data
        return True

    def get_latest_document_by_url(self, url: str) -> Optional[ExtractedDocument]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.documents.find_one({"url": url, "is_active": True}, sort=[("version", -1)])
            if doc:
                doc.pop("_id", None)
                return ExtractedDocument(**doc)
        matches = [ExtractedDocument(**v) for v in self._store["documents"].values() if v.get("url") == url and v.get("is_active", True)]
        if matches:
            matches.sort(key=lambda x: x.version, reverse=True)
            return matches[0]
        return None

    # --- 6. change_events ---
    def record_change(self, change: ContentChange) -> bool:
        data = change.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.change_events.insert_one(data)
        self._store["change_events"][change.change_id] = data
        return True

    # --- 7 & 8. research_objectives & research_runs ---
    def save_research_objective(self, obj: ResearchObjective) -> bool:
        data = obj.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.research_objectives.update_one({"objective_id": obj.objective_id}, {"$set": data}, upsert=True)
        self._store["research_objectives"][obj.objective_id] = data
        return True

    def get_research_objective(self, objective_id: str) -> Optional[ResearchObjective]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.research_objectives.find_one({"objective_id": objective_id})
            if doc:
                doc.pop("_id", None)
                return ResearchObjective(**doc)
        data = self._store["research_objectives"].get(objective_id)
        return ResearchObjective(**data) if data else None

    def record_research_run(self, run: ResearchRun) -> bool:
        data = run.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.research_runs.insert_one(data)
        self._store["research_runs"][run.run_id] = data
        return True

    # --- 9. intelligence_findings ---
    def save_insight(self, insight: MarketInsight) -> bool:
        data = insight.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.intelligence_findings.update_one({"insight_id": insight.insight_id}, {"$set": data}, upsert=True)
        self._store["intelligence_findings"][insight.insight_id] = data
        return True

    def record_insight(self, insight: MarketInsight) -> bool:
        return self.save_insight(insight)

    def get_insight(self, insight_id: str) -> Optional[MarketInsight]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.intelligence_findings.find_one({"insight_id": insight_id})
            if doc:
                doc.pop("_id", None)
                return MarketInsight(**doc)
        data = self._store["intelligence_findings"].get(insight_id)
        return MarketInsight(**data) if data else None

    def list_insights(self, min_composite_score: float = 0.0) -> List[MarketInsight]:
        if self._connected and self.db_manager.db is not None:
            query = {"scoring.composite_score": {"$gte": min_composite_score}} if min_composite_score > 0 else {}
            cursor = self.db_manager.db.intelligence_findings.find(query)
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(MarketInsight(**doc))
            return results
        return [
            MarketInsight(**v) for v in self._store["intelligence_findings"].values()
            if v.get("scoring", {}).get("composite_score", 0.0) >= min_composite_score
        ]

    # --- 10. evidence_records ---
    def add_evidence(self, evidence: SourceEvidence) -> bool:
        data = evidence.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.evidence_records.insert_one(data)
        self._store["evidence_records"][evidence.evidence_id] = data
        return True

    def get_evidence(self, evidence_id: str) -> Optional[SourceEvidence]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.evidence_records.find_one({"evidence_id": evidence_id})
            if doc:
                doc.pop("_id", None)
                return SourceEvidence(**doc)
        data = self._store["evidence_records"].get(evidence_id)
        return SourceEvidence(**data) if data else None

    def list_evidence(self, limit: int = 100) -> List[SourceEvidence]:
        if self._connected and self.db_manager.db is not None:
            cursor = self.db_manager.db.evidence_records.find().limit(limit)
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(SourceEvidence(**doc))
            return results
        return [SourceEvidence(**v) for v in list(self._store["evidence_records"].values())[:limit]]

    # --- 11. campaign_opportunities ---
    def save_campaign(self, campaign: CampaignOpportunity) -> bool:
        data = campaign.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.campaign_opportunities.update_one({"campaign_id": campaign.campaign_id}, {"$set": data}, upsert=True)
        self._store["campaign_opportunities"][campaign.campaign_id] = data
        return True

    def get_campaign(self, campaign_id: str) -> Optional[CampaignOpportunity]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.campaign_opportunities.find_one({"campaign_id": campaign_id})
            if doc:
                doc.pop("_id", None)
                return CampaignOpportunity(**doc)
        data = self._store["campaign_opportunities"].get(campaign_id)
        return CampaignOpportunity(**data) if data else None

    def list_campaigns(self, status: Optional[str] = None) -> List[CampaignOpportunity]:
        if self._connected and self.db_manager.db is not None:
            query = {"status": status} if status else {}
            cursor = self.db_manager.db.campaign_opportunities.find(query)
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(CampaignOpportunity(**doc))
            return results
        return [
            CampaignOpportunity(**v) for v in self._store["campaign_opportunities"].values()
            if not status or v.get("status") == status
        ]

    # --- 12. content_assets ---
    def save_asset(self, asset: GeneratedAsset) -> bool:
        data = asset.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.content_assets.update_one({"asset_id": asset.asset_id}, {"$set": data}, upsert=True)
        self._store["content_assets"][asset.asset_id] = data
        return True

    def get_asset(self, asset_id: str) -> Optional[GeneratedAsset]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.content_assets.find_one({"asset_id": asset_id})
            if doc:
                doc.pop("_id", None)
                return GeneratedAsset(**doc)
        data = self._store["content_assets"].get(asset_id)
        return GeneratedAsset(**data) if data else None

    def list_assets(self, review_statuses: Optional[List[str]] = None) -> List[GeneratedAsset]:
        if self._connected and self.db_manager.db is not None:
            query = {"review_status": {"$in": review_statuses}} if review_statuses else {}
            cursor = self.db_manager.db.content_assets.find(query)
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(GeneratedAsset(**doc))
            return results
        return [
            GeneratedAsset(**v) for v in self._store["content_assets"].values()
            if not review_statuses or v.get("review_status") in review_statuses
        ]

    # --- 13. agent_runs ---
    def log_agent_run(self, run: AgentRun) -> bool:
        data = run.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.agent_runs.insert_one(data)
        self._store["agent_runs"][run.run_id] = data
        return True

    # --- 14. audience_personas ---
    def upsert_persona(self, persona: AudiencePersona) -> bool:
        data = persona.model_dump()
        if self._connected and self.db_manager.db is not None:
            self.db_manager.db.audience_personas.update_one({"segment_id": persona.segment_id}, {"$set": data}, upsert=True)
        self._store["audience_personas"][persona.segment_id] = data
        return True

    def get_persona(self, segment_id: str) -> Optional[AudiencePersona]:
        if self._connected and self.db_manager.db is not None:
            doc = self.db_manager.db.audience_personas.find_one({"segment_id": segment_id})
            if doc:
                doc.pop("_id", None)
                return AudiencePersona(**doc)
        data = self._store["audience_personas"].get(segment_id)
        return AudiencePersona(**data) if data else None

    def list_personas(self, active_only: bool = True) -> List[AudiencePersona]:
        if self._connected and self.db_manager.db is not None:
            query = {"active": True} if active_only else {}
            cursor = self.db_manager.db.audience_personas.find(query)
            results = []
            for doc in cursor:
                doc.pop("_id", None)
                results.append(AudiencePersona(**doc))
            return results
        return [AudiencePersona(**v) for v in self._store["audience_personas"].values() if not active_only or v.get("active", True)]
