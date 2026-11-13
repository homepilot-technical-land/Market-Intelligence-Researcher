"""Data models for the 14 core collections of the HomePilot Market Intelligence Engine."""

from .source import IntelligenceSource, FirecrawlConfig, RateLimitConfig
from .source_candidate import SourceCandidate
from .url import DiscoveredURL
from .document import ExtractedDocument
from .change import ContentChange, SemanticDelta
from .evidence import SourceEvidence
from .insight import MarketInsight, ScoringBreakdown, TenQuestionsAnalysis, IcebergLayerAnalysis, SystemDynamicsContext
from .research import ResearchObjective, ResearchRun
from .campaign import CampaignOpportunity
from .asset import GeneratedAsset, AssetPayload
from .agent_run import AgentRun
from .persona import AudiencePersona, InfluencesOnPerceptions, BPMJourneyMapping, ThreeRsDutyAllocation

# Aliases matching collections directly
Source = IntelligenceSource
CandidateSource = SourceCandidate
Document = ExtractedDocument
ChangeEvent = ContentChange
EvidenceRecord = SourceEvidence
IntelligenceFinding = MarketInsight
ContentAsset = GeneratedAsset
Persona = AudiencePersona

__all__ = [
    "IntelligenceSource",
    "Source",
    "SourceCandidate",
    "CandidateSource",
    "FirecrawlConfig",
    "RateLimitConfig",
    "DiscoveredURL",
    "ExtractedDocument",
    "Document",
    "ContentChange",
    "ChangeEvent",
    "SemanticDelta",
    "SourceEvidence",
    "EvidenceRecord",
    "MarketInsight",
    "IntelligenceFinding",
    "ScoringBreakdown",
    "TenQuestionsAnalysis",
    "IcebergLayerAnalysis",
    "SystemDynamicsContext",
    "ResearchObjective",
    "ResearchRun",
    "CampaignOpportunity",
    "GeneratedAsset",
    "ContentAsset",
    "AssetPayload",
    "AgentRun",
    "AudiencePersona",
    "Persona",
    "InfluencesOnPerceptions",
    "BPMJourneyMapping",
    "ThreeRsDutyAllocation",
]
