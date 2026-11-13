# HomePilot Market Intelligence Engine: Taxonomy Dynamics & Authority Source Expansion

**Document Reference:** `docs/homepilot_taxonomy_dynamics_and_authority_expansion.md`  
**Components:** Dynamic Taxonomy Engine (`src/intelligence/taxonomy.py`) + Authority Source Discovery (`src/intelligence/authority_discovery.py`) + Firecrawl v1 Ingestion  
**Status:** Live & Tested (46/46 Green Tests)  
**Date:** November 2026  

---

## 1. Executive Summary: Is the Taxonomy Static or Dynamic?

The HomePilot Market Intelligence taxonomy uses a **Hybrid Architecture**:

```
                          HOMEPILOT HYBRID TAXONOMY & DISCOVERY FLYWHEEL
                          
  +-------------------------------------------------------------------------------------------------+
  |                             LEVEL 1: STATIC ARCHITECTURAL BACKBONE                              |
  |  12 Immutable Category Buckets: IRPM, HSRD, MFPL, FTBS, HPOL, PPTR, PLZN, GEIN, CBSN, HMCH...   |
  |  (Guarantees schema stability for MongoDB, PostHog telemetry, and HomePilot Mortgage Calculator) |
  +-------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +-------------------------------------------------------------------------------------------------+
  |                            LEVEL 2: DYNAMIC KEYWORD EXPANSION LAYER                             |
  |  - Starts with statutory baseline seed keywords ("help to buy", "macroprudential", "ltv")       |
  |  - Mines newly emerging phrases from live Firecrawl scrapes ("commuter county price cap")       |
  |  - Adapts to government policy updates, scheme revisions, and developer launch nomenclature     |
  +-------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +-------------------------------------------------------------------------------------------------+
  |                         LEVEL 3: AUTHORITY SOURCE EXPANSION LOOP                                |
  |  - Combines dynamic keywords with Irish domain filters: site:gov.ie, site:.ie, site:council.ie  |
  |  - Firecrawl searches the web for new authoritative sources similar to the 35 seed links        |
  |  - Discovers local planning authorities, statutory bodies, developer masterplans, and FTB hubs  |
  +-------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +-------------------------------------------------------------------------------------------------+
  |                       LEVEL 4: OPERATOR REVIEW GATE (THE 3 R's GOVERNANCE)                      |
  |  - Discovered domains are scored for authority (90–98 for statutory, 80–85 for developers)      |
  |  - Staged in 'source_candidates' collection for human validation (Role, Rule, Route)            |
  |  - Operator approves candidates -> graduates them into registered source #36, #37, etc.         |
  +-------------------------------------------------------------------------------------------------+
```

---

## 2. What Determines Dynamic Keywords?

Dynamic keywords are not random words; they are determined by three specific feedback loops:

### Loop A: Emerging Statutory Phrases in Ingested Content
When Firecrawl scrapes official Irish housing sources (such as Revenue, Department of Housing, or CCPC), the normaliser scans for new policy terminology.
* *Example:* If the government introduces a new sub-scheme or regional boundary (e.g. *"First Home commuter county price ceiling"* or *"vacant property refurbishment grant top-up"*), the compound phrase is detected and dynamically added to `FTBS` (First-Time Buyer Schemes).

### Loop B: Developer & Estate Masterplan Nomenclature
When homebuilder sources (like Glenveagh, Cairn, Seven Mills) announce new phases:
* *Example:* Terms like *"starter home release"*, *"turnkey duplex"*, *"phase 2 booking deposit"* are dynamically mined and appended to `HSRD` (Housing Supply & Residential Developments).

### Loop C: Objective-Driven Research Directives
When an operator or Grok creates a research objective (e.g., *"Investigate Navan commuter rail and housing delivery"*):
* The system pairs regional geography (`"Navan"`, `"Meath"`) with statutory terms (`"LAP zoning"`, `"serviced site"`) to form transient discovery keywords.

---

## 3. How the Pipeline Updates Search to Add Similar Authoritative Sources

The pipeline uses the **Dynamic Authority Discovery Engine** (`src/intelligence/authority_discovery.py`) to discover new sources that are similar to the original 35 seed links.

### Step-by-Step Authority Expansion Workflow

```mermaid
sequenceDiagram
    autonumber
    participant Engine as Dynamic Taxonomy Engine
    participant FC as Firecrawl Search (/v1/search)
    participant Auth as Authority Discovery Engine
    participant Repo as MongoDB (source_candidates)
    participant Operator as 2-Person Operator CLI

    Engine->>FC: Synthesize Queries (e.g., 'site:gov.ie "help to buy" "first home scheme" Meath')
    FC-->>Auth: Candidate Results (URLs, Titles, Snippets)
    Auth->>Auth: Apply Domain Scoping (Exclude IG/TikTok/X; Allow Irish sites & FB FTB groups)
    Auth->>Auth: Calculate Publisher Authority Score (90-98 for Gov, 80-85 for Devs)
    Auth->>Repo: Stage Candidates (status: "pending_approval")
    Operator->>Repo: python cli.py list-reviews / discover-authorities
    Operator->>Repo: python cli.py approve-review --id cand_id
    Repo-->>Engine: Promoted to Official Registered Source #36+
```

### Authority Scoring Matrix

| Discovered Domain Type | Examples | Calculated Authority Score | Routing Action |
|---|---|---|---|
| **Statutory Agency / Department** | `gov.ie`, `cso.ie`, `centralbank.ie`, `revenue.ie` | **95.0 – 99.0** | High-priority candidate; automatic queueing |
| **Local Planning Authority / County Council** | `meath.ie`, `kildarecoco.ie`, `fingal.ie` | **90.0 – 94.0** | Added to regional supply and LAP planning monitoring |
| **Major Institutional Research** | `esri.ie`, `scsi.ie`, `housingagency.ie` | **90.0 – 95.0** | Macroeconomic and construction cost tracking |
| **Major Residential Developer** | New homebuilder portals, masterplan microsites | **80.0 – 85.0** | Pipeline launch and starter home price monitoring |
| **Facebook FTB Community** | `facebook.com/groups/firsttimebuyersireland/` | **75.0 – 80.0** | Peer buyer questions, conveyancing friction sentiment |
| **Social Media Noise (IG/TikTok/X)** | Non-community social networks | **0.0 (Blocked)** | Strictly rejected; X reserved for xAI API |

---

## 4. Live CLI Demonstration

Operators can trigger dynamic authority discovery and review candidates directly from the CLI:

```bash
# 1. Discover new Irish authority candidates using dynamic taxonomy queries
python cli.py discover-authorities --county "Meath"

# 2. Search specifically for Facebook First-Time Buyer communities
python cli.py search-fb-communities --query "First Time Buyers Ireland" --limit 3

# 3. List candidates currently awaiting human validation in the queue
python cli.py list-reviews

# 4. Approve and promote a candidate source to the active registry
python cli.py approve-review --id "cand_meath_coco" --feedback "Approved official local authority portal"
```

---

## 5. Summary Table: Static vs. Dynamic Taxonomy Boundaries

| Architectural Component | Static or Dynamic? | What Controls It? | Purpose |
|---|---|---|---|
| **12 Core Category Codes** (`IRPM`, `FTBS`, etc.) | **Static** | System Architecture | Prevents schema corruption, database fragmentation, and contract breakage. |
| **Seed Keyword List** | **Static Baseline** | Statutory Legislation | Ensures baseline precision for mortgage and housing rules. |
| **Discovered Keyword Terms** | **Dynamic** | Scraped Firecrawl Data & Policy Changes | Adapts to changing government programs, grants, and developer phase terms. |
| **Search Query Generation** | **Dynamic** | Taxonomy Engine Synthesis | Pairs emerging terms with `site:gov.ie` and `site:.ie` to find new sources. |
| **Registered Seed Sources (35)** | **Static Baseline** | Operator Seed Registry | The validated core Irish housing and developer links. |
| **Source Candidate Promotion** | **Dynamic (Human Gated)** | 2-Person Operator Approval (3 R's) | Graduates discovered authority links into permanent sources #36, #37, etc. |
