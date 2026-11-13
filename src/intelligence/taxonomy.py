from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TaxonomyCategory:
    code: str
    name: str
    scope: str
    keywords: List[str]

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

def classify_text_category(text: str) -> str:
    """Rule-based heuristic category classifier for fallback / pre-filtering."""
    text_lower = text.lower()
    scores: Dict[str, int] = {}
    
    for code, category in TAXONOMY_REGISTRY.items():
        score = sum(1 for kw in category.keywords if kw in text_lower)
        scores[code] = score

    best_code = max(scores, key=scores.get)
    # Default to IRPM if no keywords matched
    return best_code if scores[best_code] > 0 else "IRPM"
