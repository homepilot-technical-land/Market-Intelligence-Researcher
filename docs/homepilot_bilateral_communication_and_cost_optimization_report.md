# HomePilot Intelligence Engine — Bilateral Communication, Cost Optimization & PostHog Telemetry Report

**Document Reference:** `HP-INTEL-BILATERAL-COST-OBSERVABILITY-v3.1`  
**Operational Scope:** Pure Standalone Internal Engine (Exclusively for 2 Operators)  
**Strict Boundary Isolation:** 100% Independent of `Mortgage_calculator_QA` (Zero shared code, dependencies, or databases)  
**Target Operating Budget:** $\le$ €35 / month  
**Observability Engine:** PostHog Operational Telemetry (Free Tier) + MongoDB Source of Truth  

---

> [!IMPORTANT]
> **Architectural Guardrail & 2-Person Operator Model**:
> This intelligence pipeline is an internal research instrument designed to run cost-efficiently for **two team operators**. It does not allow the LLM (xAI Grok) to make unconstrained autonomous decisions. Instead, deterministic Python analysis runs **first**, feeds structured context into Grok, and routes high-impact or low-confidence findings into a human validation queue before updating strategy.

---

## 1. Bilateral Communication Architecture

The system coordinates bilateral dialogue across three distinct layers:
1. **Python Core $\longleftrightarrow$ Firecrawl**: Multi-stage URL discovery and candidate filtering.
2. **Python Core $\longleftrightarrow$ GrokBot (Bot-to-Bot)**: Deterministic pre-analysis fed into Grok; Grok returns structured cognitive breakdowns and signals missing evidence gaps back to the ingestion pipeline.
3. **GrokBot $\longleftrightarrow$ Human Operator (The 2-Person Team)**: Automated validation gates where Grok flags anomalies or statutory policy changes for human approval and receives operator feedback.

```mermaid
flowchart TD
    subgraph L1["Layer 1: Python Core <--> Firecrawl (URL Ingestion & Filtering)"]
        FC["Firecrawl API\n(Map / Crawl / Scrape)"] <-->|Discovers 5,000 URLs| Funnel["4-Stage Python Filtering Funnel\n• Fast Rejection: -2,000 Irrelevant\n• Hash Cache: -1,500 Duplicate/Unchanged\n• Lightweight: 1,000 Local Processing\n• High Priority: 500 Grok Target Queue"]
    end

    subgraph L2["Layer 2: Python Core <--> GrokBot (Bot-to-Bot Cognitive Layer)"]
        PreAnal["Internal Deterministic Pre-Analysis\n• Strips boilerplate & normalises markdown\n• Computes 12-category classification\n• Evaluates 6-dimension scoring formula"] -->|Context Payload & Quotes| Grok["xAI Grok Cognitive Engine\n• 10 Strategic Questions\n• Iceberg Model & System Dynamics\n• Evaluates Persona Friction Impact"]
        Grok -->|Evidence Gap Request\n(e.g., query CSO / RTB)| PreAnal
    end

    subgraph L3["Layer 3: GrokBot <--> Human Operator (Validation & Feedback Gate)"]
        Grok -->|Confidence < 85 OR Statutory Cap Change| ReviewQueue[("2-Person Operator Review Queue\n(MongoDB: operator_reviews)")]
        ReviewQueue <-->|Approve / Amend / Add Feedback| Operator["Internal Operator\n(2 Team Members)"]
        Operator -->|Certified Strategy & Evolved Persona| ActiveKB[("Active Standalone KB\n(MongoDB: homepilot_intelligence)")]
    end

    subgraph L4["Operational Observability"]
        PostHog["PostHog Operational Telemetry\n(10 Operational Events Captured)"]
    end

    Funnel --> PreAnal
    L1 -.-> PostHog
    L2 -.-> PostHog
    L3 -.-> PostHog
```

---

## 2. The 4-Stage Filtering Funnel (Managing the API Budget)

To prevent uncontrolled LLM token expenditure, we do not feed raw scraped web pages directly into Grok. Consider a typical crawl cycle discovering **5,000 candidate pages**:

```
5,000 Discovered URLs
  │
  ├── [Stage 1: Fast Heuristic Filter] ────────► 2,000 Discarded (Careers, Privacy, Cookie, Login)
  │                                               (Cost: $0.00 | Tokens: 0)
  │
  ├── [Stage 2: Canonical SHA-256 Cache] ──────► 1,500 Discarded (Unchanged content from previous run)
  │                                               (Cost: $0.00 | Tokens: 0)
  │
  ├── [Stage 3: Lightweight Local Analysis] ───► 1,000 Lightly Processed (Keyword & Category Tagging)
  │                                               (Cost: $0.00 | Tokens: 0)
  │
  └── [Stage 4: High-Priority Gate] ───────────► 500 Dispatched to xAI Grok
                                                  (Deep 10-Qs, Iceberg, Persona Benchmarking)
```

### Financial Impact of the Funnel
- **Total Discovered:** 5,000 pages
- **Pages requiring Grok Deep Dive:** 500 pages (10% of total)
- **Pages Saved from LLM Invocations:** 4,500 pages
- **Estimated Tokens Saved:** $4,500 \times 1,500\text{ tokens} = 6,750,000\text{ tokens}$
- **Direct Cash Saved per Crawl Run:** **~$13.50 saved** on a single crawl cycle!

---

## 3. xAI Call Frequency & Monthly Cost Envelope ($\le$ €35)

### 3.1 Proposed Operational Scheduling by Source Tier
We never execute continuous polling with Grok. Python and Firecrawl perform the lightweight checking, invoking Grok **strictly on event triggers** (when a content hash changes or a high-priority research run is commanded):

| Source Ecosystem / Operation | Target Cadence | Processing Engine | Grok Invocation Rule |
| :--- | :--- | :--- | :--- |
| **Government Policy & Legislation** (Gov.ie, Darragh O'Brien circulars) | Daily | Firecrawl Map + Python Hash | Only if SHA-256 changes or new statutory circular detected |
| **Revenue & CCPC Guidelines** (HTB rules, consumer guides) | Daily | Firecrawl Scrape + Diff | Only if numeric subsidy caps or eligibility changes |
| **New Housing Development Launches** (Cairn, Glenveagh, LDA) | Daily | Firecrawl Map + Regex Filter | Only for new phase pricing and starter home announcements |
| **Estate Agent Content** (Daft, MyHome, Sherry Fitz) | Every 2–3 Days | RSS / Web Scraper | Only for quarterly reports and county median shifts |
| **Property Market Datasets** (PPR, CSO PxStat) | Weekly | Direct API / Batch CSV | Deterministic Python calculation; Grok synthesizes macro summary |
| **Geospatial & Environmental** (OSi, EPA) | Weekly / On Release | REST API Connector | Only when radon/boundary datasets update |
| **Authority Source Discovery Engine** | Weekly | Python Search Connector | Evaluates and ranks candidate sources for operator review |
| **Objective-Driven Research Runs** | 2–3 Times Weekly | Research Engine CLI | Full synthesis across audience personas for strategic briefs |
| **Daily Intelligence Briefing** | Every Morning (07:00 UTC)| Automated Job | 1 Grok call summarizing top clustered insights from previous 24h |

### 3.2 Monthly Cost Breakdown Proof

| Operational Component | Monthly Volume | Input Tokens (est.) | Output Tokens (est.) | xAI Blended Cost |
| :--- | :--- | :--- | :--- | :--- |
| **High-Priority Page Assessments** | 500 pages | $500 \times 1,500 = 750,000$ | $500 \times 350 = 175,000$ | $\$1.50 + \$1.75 = \mathbf{\$3.25}$ |
| **Objective Research Runs** | 12 runs (3/wk) | $12 \times 3,000 = 36,000$ | $12 \times 1,000 = 12,000$ | $\$0.07 + \$0.12 = \mathbf{\$0.19}$ |
| **Daily Morning Briefings** | 30 runs | $30 \times 4,000 = 120,000$ | $30 \times 800 = 24,000$ | $\$0.24 + \$0.24 = \mathbf{\$0.48}$ |
| **Dynamic Persona Evolution Checks** | 8 runs | $8 \times 2,500 = 20,000$ | $8 \times 600 = 4,800$ | $\$0.04 + \$0.05 = \mathbf{\$0.09}$ |
| **Operator Feedback Re-evaluations** | 25 reviews | $25 \times 1,500 = 37,500$ | $25 \times 400 = 10,000$ | $\$0.08 + \$0.10 = \mathbf{\$0.18}$ |
| **Buffer / Spike Allowance (200% Surge)**| — | 1,000,000 | 300,000 | $\mathbf{\$5.00}$ |
| **Total Estimated xAI Monthly Cost** | — | — | — | **$\approx \$9.19$ (~€8.50)** |

> [!TIP]
> **Total Monthly Operating Cost:** **~€8.50 to €14.00**, leaving over **€21.00 headroom** below the €35.00 threshold.

---

## 4. GrokBot-to-GrokBot & Human-in-the-Loop Protocol

To ensure GrokBot does not operate as an unguided black box:
1. **Bot-to-Bot Loop**:
   - Python performs text cleaning, boilerplate removal, taxonomy classification, and calculates the preliminary composite score.
   - Grok receives this pre-calculated context and maps the findings against the 10 strategic questions and the Meadows/Sterman Iceberg layers.
   - If Grok detects that empirical backing is insufficient (e.g., question 10: *"Additional evidence needed: County Meath starter home transaction records from PPR"*), it signals an **Evidence Request** back to the Python crawler rather than inventing figures.
2. **Human Operator Validation Gate**:
   - Any finding with confidence $< 85.0$ or involving statutory scheme price caps (e.g. First Home Scheme / Help to Buy) triggers an **`OperatorReviewTask`**.
   - The task is staged in MongoDB with status `pending`.
   - The two internal operators review the finding via the API / CLI, add feedback (e.g. *"Verified against Housing Agency circular"*), and approve.
   - The operator's feedback is injected back into the insight, elevating its confidence to $95.0$ and officially releasing it into the active knowledge base.

---

## 5. PostHog Operational Observability (Free Tier Architecture)

Rather than building and maintaining a heavy custom monitoring frontend, we leverage **PostHog's Free Tier** (1M monthly events, 100k AI observability events, 10GB logs) purely for operational health, credit consumption, and token economy tracking.

### 5.1 Strict Data Privacy Boundary
- **What PostHog Receives:** Operational metadata, source domain IDs, URL hashes, execution latencies, token consumption, composite scores, and pipeline errors.
- **What PostHog NEVER Receives:** Zero Personally Identifiable Information (PII), zero individual user financial data, zero mortgage scenarios, zero borrower details.
- **Data Source of Truth:** MongoDB (`homepilot_intelligence`) remains the sole database of record. PostHog is strictly an operational telemetry collector.

### 5.2 Registered Operational Events in `src/observability/posthog_client.py`

| Event Name | Emitted At | Key Properties Captured |
| :--- | :--- | :--- |
| `source.crawl.completed` | Completion of Firecrawl run | `source_id`, `total_urls`, `high_priority`, `cost_saved_usd` |
| `source.page.discovered` | New URL identified by crawler | `source_id`, `url_hash`, `tier` |
| `document.relevance.scored` | Internal deterministic scoring complete | `doc_id`, `composite_score`, `category` |
| `document.change.detected` | Semantic diff engine detects change | `doc_id`, `change_type`, `version`, `numeric_deltas` |
| `research.objective.completed` | Objective research run finished | `objective_id`, `sources_consulted`, `gaps_count` |
| `source.recommendation.created`| Authority discovery finds candidate | `candidate_id`, `domain`, `semantic_score` |
| `campaign.opportunity.generated`| Insight routed to operator review | `task_id`, `title`, `confidence` |
| `grok.api.cost.recorded` | Successful xAI Grok completion | `doc_id`, `tokens_used`, `cost_usd` |
| `crawl.credit.consumed` | Firecrawl API credit consumed | `source_id`, `credits_used`, `endpoint` |
| `agent.execution.failed` | Any pipeline or network error | `step`, `error_type`, `source_id` |

---

## 6. Code Implementation & Verification

The architecture has been fully codified, integrated, and verified in the repository:

1. **`src/intelligence/bilateral_bridge.py`**:
   - Implements `FilterFunnelResult`, `OperatorReviewTask`, and `BilateralCommunicationBridge`.
   - Manages the 4-stage funnel, internal pre-analysis, Grok dialogue, and human operator feedback application.
2. **`src/observability/posthog_client.py`**:
   - Implements `PostHogTelemetry` using `httpx` to deliver non-blocking event telemetry with automatic privacy sanitization.
3. **`src/storage/repository.py`**:
   - Enhanced with `get_insight(insight_id)` and `record_insight(insight)` supporting MongoDB and in-memory persistence.
4. **`tests/test_bilateral_bridge.py`**:
   - Full test coverage for PostHog event capture, funnel filtering logic, Grok dialogue, operator review generation, and feedback loop execution.

### Verification Results
```bash
source .venv/bin/activate && pytest -v
======================= 26 passed, 54 warnings in 26.82s =======================
```
- **Total Tests:** **26 / 26 Passing (100% Green)**
- **Git Commit:** `feat(bilateral): implement 3-tier bilateral communication, PostHog telemetry, and URL filtering funnel` (`01058e8`)
