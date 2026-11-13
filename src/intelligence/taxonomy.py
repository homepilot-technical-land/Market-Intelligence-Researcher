import re
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class TaxonomyCategory:
    code: str
    name: str
    scope: str
    keywords: List[str]
    dynamic_keywords: Set[str] = field(default_factory=set)

    @property
    def all_keywords(self) -> List[str]:
        return list(dict.fromkeys(self.keywords + sorted(list(self.dynamic_keywords))))

TAXONOMY_REGISTRY: Dict[str, TaxonomyCategory] = {
    "IRPM": TaxonomyCategory(
        code="IRPM",
        name="Irish Residential Property Markets",
        scope="Macro market trends, nationwide/county asking price movements, housing market liquidity, aggregate listing volumes.",
        keywords=["asking price", "property market", "house prices", "daft report", "myhome report", "quarterly report", "market inflation", "housing market index"]
    ),
    "HSRD": TaxonomyCategory(
        code="HSRD",
        name="Housing Supply & Residential Developments",
        scope="Active and pipeline residential schemes, phase completions, developer launch schedules, construction delivery statistics.",
        keywords=["new homes", "residential development", "phase launch", "starter homes", "units commenced", "cairn", "glenveagh", "ballymore", "lda"]
    ),
    "MFPL": TaxonomyCategory(
        code="MFPL",
        name="Mortgage & Financial Planning",
        scope="Central Bank macroprudential rules (LTI/LTV), lender interest rates (fixed/variable/green), stress-testing criteria, underwriting standards.",
        keywords=["mortgage rate", "central bank", "loan to income", "loan to value", "macroprudential", "fixed rate", "variable rate", "green mortgage", "stress test", "drawdown"]
    ),
    "FTBS": TaxonomyCategory(
        code="FTBS",
        name="First-Time Buyer Schemes",
        scope="Help to Buy (HTB), First Home Scheme (equity share), Local Authority Home Loan (LAHL), Vacant Property Refurbishment Grant.",
        keywords=["help to buy", "first home scheme", "local authority home loan", "first-time buyer", "shared equity", "grant", "revenue", "vacant property refurbishment"]
    ),
    "HPOL": TaxonomyCategory(
        code="HPOL",
        name="Housing Policy & Regulation",
        scope="Government legislation, Housing for All targets, Land Development Agency mandates, Residential Tenancies Board rules, conveyancing reforms.",
        keywords=["housing for all", "department of housing", "legislation", "policy", "statutory instrument", "conveyancing reform", "minister for housing"]
    ),
    "PPTR": TaxonomyCategory(
        code="PPTR",
        name="Property Prices & Transactions",
        scope="Verified historical transaction data, sold price analysis, stamp duty records, asking vs. achieved price deltas.",
        keywords=["property price register", "sold price", "ppr", "stamp duty", "residential transactions", "price register"]
    ),
    "PLZN": TaxonomyCategory(
        code="PLZN",
        name="Planning & Zoning",
        scope="Local Area Plans (LAPs), County Development Plans, Strategic Housing Developments (SHD/LRD), planning permissions and judicial reviews.",
        keywords=["planning permission", "zoning", "an bord pleanála", "local area plan", "lrd", "strategic housing", "planning search"]
    ),
    "GEIN": TaxonomyCategory(
        code="GEIN",
        name="Geography & Infrastructure",
        scope="Transport routes (DART+, Luas extensions, bus corridors), school capacity, flood risk designations, water infrastructure (Uisce Éireann).",
        keywords=["infrastructure", "transport", "dart+", "commuter rail", "flood risk", "epa", "osi", "uisce éireann", "water infrastructure", "greenway"]
    ),
    "CBSN": TaxonomyCategory(
        code="CBSN",
        name="Consumer Behaviour & Sentiment",
        scope="Buyer survey data, changing preferences (e.g. WFH space vs. commute), bidding patterns, buyer demographics.",
        keywords=["buyer sentiment", "consumer survey", "ccpc", "bidding", "work from home", "first-time buyer survey", "buyer concerns"]
    ),
    "HMCH": TaxonomyCategory(
        code="HMCH",
        name="Homeownership Challenges",
        scope="Conveyancing delays, chain collapses, structural defect disclosures, legal friction points, bidding war transparency issues.",
        keywords=["conveyancing delay", "legal delay", "closing costs", "structural survey", "title deeds", "bidding war", "probate delay"]
    ),
    "AFFR": TaxonomyCategory(
        code="AFFR",
        name="Affordability & Financial Readiness",
        scope="True cost of acquisition (legal, survey, stamp duty, valuation), deposit accumulation, debt-to-income hygiene, emergency buffer readiness.",
        keywords=["affordability", "deposit", "savings", "financial readiness", "hidden costs", "mortgage ready", "legal fees", "survey fee"]
    ),
    "IRMD": TaxonomyCategory(
        code="IRMD",
        name="Industry Research & Market Developments",
        scope="Economic analyses by ESRI, SCSI, Central Bank, professional commentary on construction cost inflation and materials supply.",
        keywords=["esri", "scsi", "bpfi", "construction costs", "tender prices", "housing forecast", "economic commentary"]
    )
}

class DynamicTaxonomyEngine:
    """Manages the hybrid taxonomy system:
    
    1. Static Foundation: 12 immutable category buckets ensuring schema stability.
    2. Dynamic Keyword Expansion: Identifies and incorporates emerging phrases from Firecrawl content.
    3. Authority Discovery Query Generator: Synthesizes high-yield search queries to discover new Irish
       authoritative sources similar to the 35 seed links.
    """

    def __init__(self, registry: Optional[Dict[str, TaxonomyCategory]] = None):
        self.registry = registry or TAXONOMY_REGISTRY

    def get_keywords(self, category_code: str) -> List[str]:
        """Returns all static and dynamically acquired keywords for a category."""
        category = self.registry.get(category_code)
        return category.all_keywords if category else []

    def add_dynamic_keyword(self, category_code: str, keyword: str) -> bool:
        """Adds a newly discovered keyword from Firecrawl crawls to a taxonomy category."""
        category = self.registry.get(category_code)
        if not category:
            logger.warning(f"Cannot add keyword to unknown category: {category_code}")
            return False

        clean_kw = keyword.strip().lower()
        if len(clean_kw) < 3 or clean_kw in category.keywords:
            return False

        category.dynamic_keywords.add(clean_kw)
        logger.info(f"Dynamically expanded taxonomy [{category_code}] with term: '{clean_kw}'")
        return True

    def extract_emergent_keywords(self, document_text: str, category_code: Optional[str] = None) -> List[str]:
        """Extracts candidate housing keywords from newly scraped Firecrawl markdown."""
        target_code = category_code or self.classify_text(document_text)
        category = self.registry.get(target_code)
        if not category:
            return []

        existing_keywords = set(k.lower() for k in category.all_keywords)
        text_lower = document_text.lower()

        # Housing specific domain stems to mine dynamic compound phrases
        stems = [
            r"([a-z\-]+ (?:price cap|price ceiling|relief|grant|subsidy))",
            r"((?:first home|help to buy|commuter) [a-z\-]+)",
            r"([a-z\-]+ (?:exemption|underwriting|stress test|drawdown))",
            r"((?:residential|housing|starter) [a-z\-]+)",
            r"([a-z\-]+ (?:zoning|planning permission|masterplan))"
        ]

        discovered: List[str] = []
        for stem in stems:
            matches = re.findall(stem, text_lower)
            for m in matches:
                clean_m = m.strip()
                if len(clean_m) > 4 and clean_m not in existing_keywords and clean_m not in discovered:
                    discovered.append(clean_m)

        return discovered[:8]

    def classify_text(self, text: str) -> str:
        """Classifies text into one of the 12 taxonomy categories using static and dynamic keywords."""
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        
        for code, category in self.registry.items():
            score = sum(1 for kw in category.all_keywords if kw in text_lower)
            scores[code] = score

        best_code = max(scores, key=scores.get)
        return best_code if scores[best_code] > 0 else "IRPM"

    def generate_authority_discovery_queries(
        self,
        category_code: Optional[str] = None,
        county: Optional[str] = None
    ) -> List[str]:
        """Synthesizes search queries to find new Irish authoritative sources similar to the 35 seeds.
        
        Uses dynamic taxonomy keywords with Irish institutional domain filters.
        """
        queries: List[str] = []
        target_categories = [category_code] if category_code else ["FTBS", "HSRD", "HPOL", "MFPL", "PLZN"]
        county_suffix = f" {county}" if county else ""

        for code in target_categories:
            category = self.registry.get(code)
            if not category:
                continue

            # Pick 2 distinctive keywords from the category
            kws = category.all_keywords[:3]
            kw_str = " ".join([f'"{k}"' for k in kws[:2]])
            
            # 1. Statutory and Local Government search
            queries.append(f"site:gov.ie OR site:.ie {kw_str} official guidance{county_suffix}")
            
            # 2. Local Council planning and housing delivery search
            queries.append(f"site:.ie {kw_str} housing delivery action plan{county_suffix}")
            
            # 3. Major residential scheme & developer announcements
            queries.append(f"site:.ie {kw_str} new residential development launch{county_suffix}")

        return list(dict.fromkeys(queries))

def classify_text_category(text: str) -> str:
    """Backward-compatible functional helper for heuristic category classification."""
    engine = DynamicTaxonomyEngine()
    return engine.classify_text(text)
