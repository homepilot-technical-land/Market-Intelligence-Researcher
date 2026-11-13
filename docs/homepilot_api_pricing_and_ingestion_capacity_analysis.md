# HomePilot Market Intelligence — Ingestion Capacity & Budget Architecture (Firecrawl + xAI API)

**Document Reference:** `HP-INTEL-CAPACITY-XAI-FIRECRAWL-v2.0`  
**Operational Scope:** Internal Financial & Ingestion Capacity Analysis (Dedicated for 2 Operators)  
**Strict Boundary Isolation:** 100% Independent of `Mortgage_calculator_QA` (Zero shared code, databases, or policies)  
**Target Monthly Operating Budget:** 
- **Firecrawl API:** ~€14 / month (Hobby Plan, 5,000 credits/pages)
- **xAI API (Grok API Tokens):** €25 / month (~$27 USD token usage)
- **Database & Hosting (MongoDB/Redis):** $\le$ €10 / month (effectively €0–€5 on free/starter tiers)
- **Grok Bot Base:** Already paid / existing subscription (no additional tool fee accounted)

---

> [!IMPORTANT]
> **Clarification on Tooling**:
> This model evaluates **xAI API** (the direct developer API for Elon Musk's Grok from `api.x.ai`) and **Firecrawl API**. Because Grok Bot is already paid for by the team, the €25 is dedicated entirely to **xAI API inference tokens** (programmatic calls from Python).

---

## 1. Executive Summary: Monthly Information Throughput

With **€14 on Firecrawl** and **€25 on the xAI API**, the system achieves complete market coverage for the Irish homeownership operating system:

| Layer / Service | Monthly Cost | Monthly Capacity / Quota | Ingestion & Internal Processing Capacity |
| :--- | :--- | :--- | :--- |
| **Firecrawl API** | **~€14.00 – €16.00** | **5,000 credits / month**<br>(Hobby Plan, 5 concurrent browsers) | **5,000 full authority web pages** scraped to clean markdown across our 34 registered seed domains. |
| **Open Public APIs** (PPR, CSO, RTB) | **€0.00** (Free statutory data) | Unlimited batch downloads | Thousands of quarterly transaction records and rent index benchmarks. |
| **Python Deterministic Engine** | **€0.00** (Runs locally / in-process) | All 5,000 pages + datasets | • Boilerplate stripping & SHA-256 deduplication<br>• 12-category taxonomy classification<br>• 6-dimension composite scoring<br>• Semantic diff & numerical price delta tracking |
| **MongoDB Atlas & Redis** | **€0.00 – €5.00** (< €10 target) | 512 MB M0 sandbox (Free)<br>Upstash Redis (Free) | **20,000 to 25,000 document snapshots** stored with complete version history and zero license costs. |
| **xAI API (Grok Tokens)** | **€25.00** (~$27.00 USD) | Token usage @ $2.00/1M input & $10.00/1M output | **Up to 3,850 full cognitive breakdowns** (10 Strategic Questions, Iceberg root causes, and persona benchmarking). |
| **Total Monthly** | **~€39 – €46 / month** | — | **5,000 pages ingested $\rightarrow$ 100% analyzed internally $\rightarrow$ 1,500–3,800 deep Grok cognitive syntheses.** |

---

## 2. Firecrawl API Ingestion Breakdown (€14 / 5,000 Pages)

### 2.1 The Credit Economics
- **Cost:** $19/mo (monthly) or $16/mo (annual, approx. **€14.70/month**).
- **Allowance:** **5,000 credits** per month.
- **Consumption:**
  - Standard page scrape (`/v1/scrape` returning markdown): **1 credit per page**.
  - Site mapping (`/v1/map`): **1 credit per 100 discovered URLs**.
  - Deep crawl (`/v1/crawl`): **1 credit per page**.

### 2.2 Preserving the Full 5,000 Page Allowance
> [!TIP]
> **Anti-Waste Architecture**:
> Firecrawl charges **+4 credits per page** if you request their built-in LLM structured extraction (consuming 5 credits per page, cutting 5,000 pages down to 1,000).
> **We never use Firecrawl's LLM extraction**. Firecrawl is used strictly to bypass dynamic JavaScript and deliver clean markdown (1 credit/page). Our internal Python Document Normaliser and xAI Grok API perform the structured extraction at 1/10th of the cost.

### 2.3 What 5,000 Monitored Pages Covers in Ireland
5,000 pages/month provides comprehensive monitoring across the 6 Irish property ecosystems:
- **34 Registered Seed Domains:** (Gov.ie, CCPC, Central Bank, Housing Agency, Daft, MyHome, Cairn, Glenveagh, LDA).
- If each seed domain has 20–30 priority monitoring paths checked weekly:
  $$34\text{ domains} \times 25\text{ pages} \times 4\text{ weeks} = 3,400\text{ page scrapes/month}$$
- Leaves **1,600 credits/month** for ad-hoc deep crawling of newly launched residential schemes, county development plans, or newly discovered authority sites.

---

## 3. xAI API Token Economics (€25 / ~$27 USD)

With the Grok Bot subscription already paid for by the team, the entire **€25 (~$27 USD)** is applied directly to **xAI API tokens** (`api.x.ai`).

### 3.1 xAI API Pricing Rates
- **Input Tokens:** **$2.00 per 1,000,000 tokens** ($0.000002 / token).
- **Output Tokens:** **$10.00 per 1,000,000 tokens** ($0.000010 / token).
- *(If using Fast/Mini tier for rapid filtering: $0.20/1M input, $0.50/1M output).*

### 3.2 Unit Cost per Document Analysis
For a standard high-priority intelligence analysis, the Python pre-normaliser delivers a compact context payload:
- **Prompt Input:** ~1,500 tokens (document title, pre-classified category, numerical diffs, evidence quote, and system prompt).
- **Completion Output:** ~400 tokens (answers to the 10 Strategic Questions, Iceberg root causes, stock/flow impact, persona hook).

$$\text{Cost per Grok Analysis} = (1,500 \times \$0.000002) + (400 \times \$0.000010) = \$0.003 + \$0.004 = \mathbf{\$0.007\text{ (less than 1 cent)}}$$

### 3.3 How Many Pages Can xAI Grok Analyze for €25?

$$\text{Total Invocations} = \frac{\$27.00\text{ USD}}{\$0.007\text{ per page}} = \mathbf{3,857\text{ Deep Cognitive Analyses / Month}}$$

**This is a critical finding:**
Your €25 xAI API budget allows you to run **over 3,850 deep cognitive analyses per month**. 
Since Firecrawl only collects 5,000 pages, and your Python filtering funnel eliminates ~1,500–2,000 duplicates or unchanged pages, **you have enough xAI budget to analyze virtually every single changed or relevant page Firecrawl ever collects!**

---

## 4. The End-to-End Processing Funnel (5,000 Pages $\rightarrow$ Strategy)

Here is how the 5,000 pages from Firecrawl flow through your internal system and xAI Grok:

```
+-----------------------------------------------------------------------------------+
|                        THE MONTHLY INGESTION WORKFLOW                             |
+-----------------------------------------------------------------------------------+
|  1. RAW COLLECTION (Firecrawl API - €14):                                         |
|     • 5,000 authority pages scraped to clean markdown                             |
|                                │                                                  |
|  2. PYTHON DETERMINISTIC PRE-ANALYSIS (Zero AI Cost):                             |
|     • Step A: SHA-256 Hashing -> Identifies ~1,500 unchanged pages (0 LLM cost)   |
|     • Step B: Fast Discard -> Filters ~1,000 irrelevant utility pages (0 LLM cost)|
|     • Step C: 12-Category Classification -> Applied to all remaining 2,500 pages  |
|     • Step D: 6-Dimension Scoring -> Computes composite 0-100 score locally       |
|                                │                                                  |
|  [NET ACTIVE CANDIDATES: ~2,500 modified or relevant pages]                       |
|                                │                                                  |
|  3. COGNITIVE DEEP DIVE (xAI API - €25 budget):                                   |
|     • Dispatches all Top High-Priority Pages (composite score >= 70)              |
|     • Evaluates ~1,000 to 1,500 priority pages:                                  |
|       1,500 pages x $0.007 = $10.50 USD (~€9.70)                                  |
|                                │                                                  |
|  4. SURPLUS xAI BUDGET DEPLOYMENT (€15.30 remaining):                             |
|     • 30 Daily Morning Briefings (30 x $0.016 = $0.48)                            |
|     • 15 Objective-Driven Research Runs (15 x $0.025 = $0.38)                     |
|     • Dynamic Persona Evolution Checks across 5 marketing segments ($1.50)        |
|     • Headroom / Surge Buffer ($12.00+ remaining unused)                          |
+-----------------------------------------------------------------------------------+
```

---

## 5. Storage Economics: Keeping Infrastructure Under €10

For a 2-person internal operation, infrastructure costs are virtually zero:

1. **MongoDB Atlas (Source of Truth)**:
   - **M0 Sandbox:** Free tier includes **512 MB storage**.
   - Average clean markdown document: 15–20 KB.
   - 512 MB holds **20,000 to 25,000 document snapshots** with version history.
   - **Cost:** **€0.00 / month**.
   - *(Even if scaling to M2 in Year 2: only $9/mo).*
2. **Redis Coordination**:
   - **Upstash Serverless Redis:** Free tier includes **10,000 commands/day**.
   - Operating 8 internal priority queues consumes ~3,000 commands/day.
   - **Cost:** **€0.00 / month**.
3. **Application Hosting**:
   - Running the monitor locally or on a lightweight Render/Railway starter service costs **€0.00 to €5.00 / month**.

---

## 6. Strategic Takeaways & Recommendations

1. **Firecrawl Hobby Plan (€14/mo) is the exact right size**: 5,000 pages per month perfectly covers daily and weekly monitoring of all 34 known Irish housing authorities and developers.
2. **€25 on xAI API is more than enough**: Because you pay ~$0.007 per analysis, €25 buys nearly 3,850 Grok analyses. You will only consume about **€10–€12/month** on Grok for actual changed content, leaving the rest as a buffer for deep research briefs.
3. **Internal Analysis Throughput**:
   - **5,000 pages** collected by Firecrawl.
   - **5,000 pages** analyzed and indexed internally by Python at zero cost.
   - **~1,200–1,500 high-priority pages** given full cognitive breakdown by Grok.
   - **All stored safely in MongoDB** under €10/month total infrastructure overhead.
