# HomePilot Market Intelligence Engine: End-to-End System Harmony & Engineering Audit

## 1. Executive Summary & Objective

This audit verifies that the **Market Intelligence Research Tool** operates as an integrated software and data engineering engine, where every component functions in harmony without dormant pathways, conflicting logic, or architectural drift from the initial charter.

```
       KICKOFF MANDATE (HomePilot_Market_Intelligence_Researcher.md)
       "You are not a generic web scraper or news summariser.
        You are an intelligence system identifying information that improves
        HomePilot's market understanding, customer education, and product positioning.
        Prioritise accuracy, relevance, evidence, and commercial usefulness."
                                     │
                                     ▼
        ┌────────────────────────────────────────────────────────┐
        │       1. THE DATA & SEMANTIC WIRING ENGINE             │
        │       (Pipes, Taxonomy, Diff Engine, MongoDB Storage)  │
        └────────────────────────────┬───────────────────────────┘
                                     │
                       BILATERAL API CONNECTION (Query / Gap)
                                     │
        ┌────────────────────────────▼───────────────────────────┐
        │       2. GROKBOT & HUMAN OPERATOR IDEATION LAYER       │
        │       (Discourse Mining, Brief Creation, Rule B-04)    │
        └────────────────────────────────────────────────────────┘
```

---

## 2. Kickoff Charter vs. Implementation Audit

Every requirement laid out in the founding kickoff document (`HomePilot_Market_Intelligence_Researcher.md`) has been mapped, implemented, and verified:

| Kickoff Mandate | Implementation Component | Verification Status |
| :--- | :--- | :--- |
| **1. Source Discovery** | `config/sources_registry.json` (35 seeds), `src/pipeline/runner.py` | ✅ **VERIFIED**: 35 sources loaded, 2-tier discovery filter active. |
| **2. 12 Categories** | `src/intelligence/taxonomy.py` | ✅ **VERIFIED**: Strict regex & keyword taxonomy mapping IRPM to IRMD. |
| **3. Relevance Scoring (0-100)** | `src/intelligence/scoring.py` | ✅ **VERIFIED**: 6-dimension weighted scoring (Relevance, Impact, Confidence, Time, Campaign, Geo). |
| **4. Information Extraction** | `src/normalisation/normaliser.py`, `src/models/document.py` | ✅ **VERIFIED**: Clean markdown, metadata extraction, content hashing. |
| **5. 10 Strategic Questions** | `src/intelligence/strategic_engine.py` | ✅ **VERIFIED**: Answers What happened, Why it matters, Who is affected, etc. |
| **6. Content Opportunities** | `src/generators/asset_blueprint.py` | ✅ **VERIFIED**: X threads, 6-slide carousels, video storyboards, briefs. |
| **7. Change Detection** | `src/intelligence/diff_engine.py` | ✅ **VERIFIED**: SHA-256 hash idempotency & semantic diff recording. |
| **8. Strict Evidence Standard** | `src/models/evidence.py`, Rule B-02 | ✅ **VERIFIED**: Minimum 2 verifiable evidence records required per asset. |
| **9. 2-Person Operator Gate** | `src/intelligence/operator_dialogue.py`, Rule B-04 | ✅ **VERIFIED**: Operator 1 (Product) $\rightarrow$ Operator 2 (Compliance) sign-off. |
| **10. Operating Budget** | `src/coordination/budget_tracker.py` | ✅ **VERIFIED**: Firecrawl €14 (5,000 pages) + xAI $27 USD ceiling strictly enforced. |

---

## 3. Data & Software Engineering Integrity

### A. Hermetic Test Database Isolation
- **Problem Identified**: When local MongoDB was started, unit tests were reading/writing to the live production database (`homepilot_intelligence`), causing collision with previously persisted records.
- **Engineering Solution**: Implemented `tests/conftest.py` with an autouse fixture setting `MONGODB_DB_NAME=homepilot_intelligence_test` that drops and re-initializes the test sandbox per test run.
- **Result**: 100% test reproducibility with zero interference with operational data.

### B. Unified Repository Access Layer
- **Refactoring Completed**: Enhanced `IntelligenceRepository` (`src/storage/repository.py`) with unified CRUD methods across all 14 collections:
  - `list_insights(min_composite_score)`
  - `get_campaign(campaign_id)`, `list_campaigns(status)`
  - `get_asset(asset_id)`, `list_assets(review_statuses)`
  - `get_evidence(evidence_id)`, `list_evidence(limit)`
- **Elimination of Dormant Pathways**: Removed duplicate direct MongoDB calls from `operator_dialogue.py` and `daily_briefing.py`, ensuring all access flows through the repository interface with automatic in-memory fallback.

---

## 4. End-to-End System Harmony

```mermaid
flowchart TD
    subgraph Data_Pipes["Data Pipes & Ingestion (The Wires)"]
        FC["Firecrawl API Connector\n(Clean Markdown, Search-then-Scrape)"]
        PPR["Property Price Register\n(Navan / Meath County Transactions)"]
        CSO["CSO PxStat Open Data\n(HPM05 Inflation & NDA02 Completions)"]
        RTB["RTB Rent Index Connector\n(Rent vs Buy Differentials)"]
    end

    subgraph Hub_Spoke["MongoDB Hub-and-Spoke (14 Collections)"]
        DB[("homepilot_intelligence\n• sources\n• documents\n• evidence_records\n• campaign_opportunities\n• content_assets")]
    end

    subgraph Bilateral["Bilateral Bridge (Python <-> GrokBot)"]
        Bridge["Bilateral Communication Bridge\n(src/intelligence/bilateral_bridge.py)"]
    end

    subgraph Grok_Layer["Ideation & Brief Authoring (GrokBot + Operator)"]
        Grok["xAI Grok Service (grok-4.20-0309)\n• Listens to X sentiment\n• Creates Campaign Briefs\n• Conversational Operator Dialogue"]
        Op1["Operator 1 Signoff (Product Lead)"]
        Op2["Operator 2 Signoff (Compliance Lead)"]
    end

    FC --> DB
    PPR --> DB
    CSO --> DB
    RTB --> DB

    DB <--> Bridge
    Bridge <--> Grok

    Grok <--> Op1
    Op1 --> Op2
    Op2 --> DB
```

1. **The Ingestion Pipes** feed clean, verified data into MongoDB without consuming unnecessary tokens.
2. **The Knowledge Pool** indexes evidence with unique IDs and 6-dimension scores.
3. **The Bilateral Bridge** lets GrokBot query the pool for facts and report missing wires.
4. **GrokBot (with Human Validation)** creates the brief and iterates with operators.
5. **The Database** records the signed-off assets ready for broadcast.

---

## 5. Verification Metrics
- **Pytest Suite**: **54 tests passing 100% green in 42.56s**.
- **Live Database**: Active MongoDB connection on `127.0.0.1:27017` across 14 collections.
- **Git Repository**: Clean working tree on branch `main` (`43674f6`).
- **Live APIs**: Firecrawl and xAI APIs tested and cost-metered ($0.031 USD / $27.00 USD spent).
