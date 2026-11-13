import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from urllib.parse import urlparse

from src.models.source_candidate import SourceCandidate
from src.storage.repository import IntelligenceRepository
from src.intelligence.taxonomy import DynamicTaxonomyEngine
from src.connectors.firecrawl_connector import FirecrawlConnector

logger = logging.getLogger(__name__)

class AuthoritySourceDiscoveryEngine:
    """Discovers, evaluates, and recommends authoritative Irish information sources to close research gaps."""

    CURATED_AUTHORITY_TARGETS = [
        {
            "candidate_id": "cand_cso_housing",
            "name": "Central Statistics Office (CSO)",
            "root_url": "https://www.cso.ie/en/statistics/housingandhouseholds/",
            "ecosystem": "Government and policy intelligence",
            "publisher_identity": "Statutory Agency (National Statistics)",
            "base_authority": 98.0,
            "justification": "Primary official statistical record for new dwelling completions, planning permissions, and Residential Property Price Index (RPPI).",
            "identified_gap": "Official macro completions and demographic household formation rates."
        },
        {
            "candidate_id": "cand_rtb_rent_index",
            "name": "Residential Tenancies Board (RTB)",
            "root_url": "https://rtb.ie/research/rent-index",
            "ecosystem": "Property market intelligence",
            "publisher_identity": "Statutory Agency (Rental Market Regulator)",
            "base_authority": 95.0,
            "justification": "Official registered tenancy rental price index. Essential for calculating rent-vs-buy economics for HomePilot users.",
            "identified_gap": "Actual standardized monthly rents paid across Local Electoral Areas (LEAs)."
        },
        {
            "candidate_id": "cand_housing_agency",
            "name": "The Housing Agency",
            "root_url": "https://www.housingagency.ie/housing-information",
            "ecosystem": "Housing supply and development intelligence",
            "publisher_identity": "State Agency",
            "base_authority": 92.0,
            "justification": "Provides national housing policy coordination, multi-unit developments guidance, and affordability research.",
            "identified_gap": "Affordable housing delivery benchmarks and local authority schemes."
        },
        {
            "candidate_id": "cand_esri_research",
            "name": "Economic and Social Research Institute (ESRI)",
            "root_url": "https://www.esri.ie/research/housing",
            "ecosystem": "Industry and competitive intelligence",
            "publisher_identity": "Independent Research Organisation",
            "base_authority": 94.0,
            "justification": "Peer-reviewed macroeconomic modelling of structural housing demand and household wealth accumulation.",
            "identified_gap": "Long-term structural housing demand estimates and interest rate transmission."
        },
        {
            "candidate_id": "cand_central_bank_macroprudential",
            "name": "Central Bank of Ireland",
            "root_url": "https://www.centralbank.ie/financial-system/financial-stability/macro-prudential-policy/mortgage-measures",
            "ecosystem": "Government and policy intelligence",
            "publisher_identity": "Statutory Regulator / Central Bank",
            "base_authority": 99.0,
            "justification": "Sole regulator of macroprudential mortgage measures (LTI and LTV limits), lender lending rules, and systemic risk.",
            "identified_gap": "Authoritative mortgage lending exemption volumes and borrower stress metrics."
        },
        {
            "candidate_id": "cand_an_coimisiun_pleanala",
            "name": "An Coimisiún Pleanála (formerly An Bord Pleanála)",
            "root_url": "https://www.pleanala.ie/en-ie/home",
            "ecosystem": "Geographic and planning intelligence",
            "publisher_identity": "Independent Statutory Planning Appeals Body",
            "base_authority": 96.0,
            "justification": "Decisions on Strategic Housing Developments (SHD), Large-Scale Residential Developments (LRD), and appeals.",
            "identified_gap": "Judicial reviews, planning approval timelines, and pipeline fallout rates."
        }
    ]

    def __init__(
        self,
        repository: Optional[IntelligenceRepository] = None,
        taxonomy_engine: Optional[DynamicTaxonomyEngine] = None
    ):
        self.repo = repository or IntelligenceRepository()
        self.taxonomy = taxonomy_engine or DynamicTaxonomyEngine()

    def identify_research_gaps(self) -> List[str]:
        """Identifies systemic data and market gaps based on existing source coverage."""
        return [
            "Official macro completions and demographic household formation rates",
            "Standardised county and Local Electoral Area rental price movements (rent-vs-buy)",
            "Macroprudential exemption drawdown ratios and interest-rate sensitivities",
            "Major planning appeal decisions and judicial review bottlenecks"
        ]

    def discover_and_evaluate_candidates(self) -> List[SourceCandidate]:
        """Discovers candidate sources, scores publisher authority, and logs for human review."""
        candidates: List[SourceCandidate] = []
        for target in self.CURATED_AUTHORITY_TARGETS:
            candidate = SourceCandidate(
                candidate_id=target["candidate_id"],
                name=target["name"],
                root_url=target["root_url"],
                ecosystem=target["ecosystem"],
                publisher_identity=target["publisher_identity"],
                authority_score=target["base_authority"],
                justification=target["justification"],
                identified_gap=target["identified_gap"],
                review_status="pending_approval",
                discovered_at=datetime.now(timezone.utc)
            )
            self.repo.add_candidate_source(candidate)
            candidates.append(candidate)

        logger.info(f"Discovered and evaluated {len(candidates)} authoritative candidate sources.")
        return candidates

    def discover_sources_via_firecrawl(
        self,
        connector: FirecrawlConnector,
        max_queries: int = 2,
        county: Optional[str] = "Meath"
    ) -> List[SourceCandidate]:
        """Uses dynamically generated taxonomy queries to discover new Irish authoritative sources via Firecrawl.
        
        Evaluates discovered domains, filters against routing policies, and stages for operator approval.
        """
        queries = self.taxonomy.generate_authority_discovery_queries(county=county)[:max_queries]
        new_candidates: List[SourceCandidate] = []
        existing_sources = {s.root_url.lower() for s in self.repo.list_sources()}
        existing_candidates = {c.root_url.lower() for c in self.repo.list_candidate_sources()}

        for query in queries:
            results = connector.search(query=query, limit=5)
            for res in results:
                url = res.get("url", "")
                title = res.get("title", "")
                desc = res.get("description", "")

                # 1. Check domain policy (no Instagram/TikTok/X; allow Irish sites & FB FTB groups)
                if not connector.is_permitted_url(url=url, title=title, description=desc):
                    continue

                # 2. Extract root domain
                parsed = urlparse(url)
                root_url = f"{parsed.scheme}://{parsed.netloc}/"

                if root_url.lower() in existing_sources or root_url.lower() in existing_candidates:
                    continue

                # 3. Calculate authority score based on publisher domain characteristics
                domain = parsed.netloc.lower()
                if "gov.ie" in domain or "cso.ie" in domain or "centralbank.ie" in domain:
                    auth_score = 96.0
                    publisher_type = "Statutory Authority / Government Body"
                elif "council.ie" in domain or "coco.ie" in domain:
                    auth_score = 92.0
                    publisher_type = "Local Planning Authority"
                elif "facebook.com" in domain and "/groups/" in url.lower():
                    auth_score = 78.0
                    publisher_type = "Buyer Community Discussion Hub"
                elif any(agent in domain for agent in ["sherryfitz", "dng", "savills", "cairnhomes", "glenveagh"]):
                    auth_score = 85.0
                    publisher_type = "Major Residential Developer / Estate Broker"
                else:
                    auth_score = 80.0
                    publisher_type = "Irish Property Market Publisher"

                candidate_id = f"cand_{domain.replace('.', '_')}"
                cand = SourceCandidate(
                    candidate_id=candidate_id,
                    name=title or domain,
                    root_url=root_url,
                    ecosystem="Housing supply and development intelligence",
                    publisher_identity=publisher_type,
                    authority_score=auth_score,
                    justification=f"Discovered via dynamic taxonomy search: '{query}'. Snippet: {desc[:100]}",
                    identified_gap=f"Regional coverage expansion for {county or 'Ireland'}",
                    review_status="pending_approval",
                    discovered_at=datetime.now(timezone.utc)
                )

                self.repo.add_candidate_source(cand)
                new_candidates.append(cand)
                existing_candidates.add(root_url.lower())

        logger.info(f"Discovered {len(new_candidates)} new candidate sources via Firecrawl dynamic search.")
        return new_candidates
