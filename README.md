# HomePilot Market Intelligence Researcher & Cognitive Pipeline

Autonomous, multi-source Irish real estate intelligence, statutory policy monitor, and strategic campaign engine designed for the HomePilot Homeownership Operating System.

[![Tests](https://img.shields.io/badge/Tests-85%20Passing-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](requirements.txt)
[![MCP](https://img.shields.io/badge/MCP-Standard%202.3-purple.svg)](src/mcp_server.py)
[![Database](https://img.shields.io/badge/MongoDB-14%20Collections-green.svg)](src/storage/mongo_client.py)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20RFC%207807-teal.svg)](src/api/intelligence_api.py)

---

## 1. Overview & System Purpose

The **HomePilot Market Intelligence Researcher** is an internal intelligence instrument operated by a 2-person leadership team (Product Lead & Legal/Compliance Lead). 

Unlike generic scrapers, it continuously discovers, monitors, sanitizes, scores, and synthesizes empirical Irish property and financial developments across:
1. **Public Macro Data**: Central Statistics Office (CSO PxStat API for HPM05 Property Price Index and NDA02 New Dwellings Completions).
2. **Transaction Registries**: Property Price Register (PPR) county-level starter and mover prices.
3. **Statutory Grant Ceilings**: First Home Scheme (FHS) price caps, Help to Buy (HTB) rules, and Central Bank macroprudential lending limits.
4. **Market Rents**: RTB Rent Index data and buy-vs-rent cash flow comparisons.
5. **Real-Time Discourse**: xAI Grok API (GrokBot) on X and Reddit OAuth 2.0 discussions across Irish homebuyer communities.

---

## 2. Architecture & Pipeline Lifecycle

The system operates across a 7-stage deterministic funnel backed by 14 Hub-and-Spoke MongoDB collections (with automatic zero-config memory fallback):

```mermaid
flowchart TD
    subgraph S1["1. Multi-Source Ingestion & Discovery"]
        Seeds["35 Approved Irish Sources\n(Gov.ie, Central Bank, Daft, MyHome, CCPC)"]
        FC["Firecrawl API\n(Map / Crawl / Scrape)"]
        PublicAPI["Live Macro Connectors\n(CSO PxStat, PPR, RTB Index)"]
        SocialConn["Social Connectors\n(Reddit OAuth 2.0, xAI Grok on X)"]
    end

    subgraph S2["2. Sanitisation & Normalisation"]
        PII["PII Scrubbing Guard\n(Zero-Leakage of Names, Emails, Phone)"]
        Norm["Markdown Normaliser & Boilerplate Stripper"]
    end

    subgraph S3["3. Cognitive Scoring & Diff"]
        Tax["12-Category Irish Taxonomy Classifier"]
        Score["6-Dimension Composite Scoring (0–100)"]
        Diff["Semantic Diff Engine (Content Hash Caching)"]
    end

    subgraph S4["4. Campaign Synthesis & Blueprinting"]
        Clust["Theme Clustering Engine\n(Cross-County Benchmark Synthesis)"]
        Blue["Asset Blueprint Generator\n(Rule B-02: Double Citation Enforced)"]
    end

    subgraph S5["5. Operational Gates & Review"]
        Grok["GrokBot MCP Dialogue\n(Interactive Asset Revision)"]
        Review["Rule B-04 Dual Signoff Gate\n(Operator 1: Product | Operator 2: Legal)"]
    end

    Seeds --> FC
    FC --> PII
    PublicAPI --> Clust
    SocialConn --> Clust
    PII --> Norm --> Tax --> Score --> Diff --> Clust --> Blue --> Grok --> Review
```

---

## 3. Key Capabilities

* **Dynamic Campaign-Driven Regional Batching**: Automatically aligns the 07:00 UTC morning intelligence brief to the active marketing campaign's focus counties (e.g. Meath, Kildare, Wicklow).
* **Out-of-Focus Anomaly Radar**: Detects regulatory shifts, planning refusals, or price surges in non-focus counties and flags them as priority alerts.
* **Native Model Context Protocol (MCP) Server**: Provides external agents (GrokBot, Claude Desktop, Cursor) with native tools to query live property data and submit knowledge gaps over `stdio` or `streamable-http`.
* **Budget & Quota Governance**: Hard limits guarding monthly external API costs (€14 Firecrawl ceiling, €25 xAI Grok ceiling) with automatic rate limiting and telemetry tracking.
* **Hermetic Resilience**: Safe startup and in-memory fallback ensure the system runs seamlessly even if MongoDB or external credentials are temporarily offline.

---

## 4. Repository Structure

```
.
├── config/
│   ├── sources_registry.json         # 35 approved Irish seed sources with cadences & tiers
│   └── budget_and_quota_policy.json  # Hard spending limits & token cost weights
├── docs/                             # Complete 31-document architectural archive
├── src/
│   ├── api/                          # FastAPI REST service with RFC 7807 problem details
│   ├── connectors/                   # Firecrawl, CSO, PPR, RTB, and Reddit API connectors
│   ├── coordination/                 # Budget governance tracker and Redis queue manager
│   ├── generators/                   # Asset blueprint builder (Rule B-02 citation enforcement)
│   ├── intelligence/                 # Taxonomy, scoring, Grok service, theme clustering, briefing
│   ├── models/                       # Pydantic data schemas across all 14 core domain models
│   ├── normalisation/                # Document normaliser and PII scrubbing engine
│   ├── pipeline/                     # 7-stage pipeline orchestrator (MarketIntelligencePipeline)
│   ├── scheduling/                   # 24/7 background daemon (briefings, cadence, gap processor)
│   ├── storage/                      # Unified MongoDB repository with memory fallback
│   └── mcp_server.py                 # MCP Server (stdio, streamable-http, SSE)
├── tests/                            # Comprehensive hermetic test suite (85 tests)
├── .github/workflows/
│   ├── ci.yml                        # Automated pull request and push test runner
│   └── scheduled_intelligence_scour.yml # Nightly 02:00 UTC automated intelligence scour
├── cli.py                            # Operator CLI (daemon, review, clustering, research)
├── render.yaml                       # Multi-service Render cloud deployment blueprint
└── run_mcp_tunnel.sh                 # Local Cloudflare tunnel runner for GrokBot MCP access
```

---

## 5. Getting Started

### Prerequisites
* Python 3.12+
* Node.js 18+ (if running the companion application service)
* Optional: MongoDB Atlas or local MongoDB instance (`mongodb://localhost:27017`)
* Optional: Redis instance (`redis://localhost:6379`)

### Installation
```bash
# Clone the repository
git clone https://github.com/samson-ade/homepilot-technical-land.git
cd "External Website Research Tool"

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration
Copy `.env.example` to `.env` and provide your credentials:
```bash
cp .env.example .env
```
Key configuration parameters:
```ini
# External Cognitive & Crawling APIs
FIRECRAWL_API_KEY=fc-...
XAI_API_KEY=xai-...
GROK_MODEL=grok-4.20-0309-non-reasoning

# Database & Cache (Optional - fallback to memory if offline)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/marketintelligenceresearch
MONGODB_DB_NAME=marketintelligenceresearch
REDIS_URL=redis://localhost:6379

# Service Ports & Environment
PORT=8001
ENVIRONMENT=development
```

---

## 6. Running the System

### 1. Execute an Autonomous Scour Cycle (On-Demand)
```bash
python cli.py run-daemon --once
```
*Auto-bootstraps approved seeds, checks source cadences, fetches macro data, clusters signals, and compiles the daily morning brief.*

### 2. Run the 24/7 Background Scheduler Daemon
```bash
python cli.py run-daemon --interval 3600
```

### 3. Launch the MCP Server
```bash
# Interactive / Remote mode (starts HTTP server on port 8001)
python src/mcp_server.py --transport streamable-http --port 8001

# Or launch with Cloudflare Tunnel for live GrokBot mobile/web access
./run_mcp_tunnel.sh
```

### 4. Connect MCP to Claude Desktop
Add this entry to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "homepilot_intelligence": {
      "command": "/absolute/path/to/External Website Research Tool/.venv/bin/python",
      "args": [
        "/absolute/path/to/External Website Research Tool/src/mcp_server.py"
      ],
      "env": {
        "MONGODB_URI": "mongodb://localhost:27017/marketintelligenceresearch",
        "MONGODB_DB_NAME": "marketintelligenceresearch"
      }
    }
  }
}
```

### 5. Launch the FastAPI Intelligence Web Service
```bash
uvicorn src.api.intelligence_api:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation (Swagger UI): `http://localhost:8000/docs`
* Built-in GrokBot Chat UI: `http://localhost:8000/chat`
* Mountable MCP Endpoint: `http://localhost:8000/mcp`

### 6. Operator Review CLI (Rule B-04 Dual Signoff)
```bash
# List assets pending operator review
python cli.py operator-review --action list

# Sign off asset as Operator 1 (Product Lead)
python cli.py operator-review --action approve-op1 --asset-id <ASSET_ID> --operator operator_1 --notes "Approved narrative focus"

# Sign off asset as Operator 2 (Compliance Lead)
python cli.py operator-review --action approve-op2 --asset-id <ASSET_ID> --operator operator_2 --notes "Verified against Central Bank guidelines"
```

---

## 7. Testing & Verification

Run the comprehensive hermetic test suite:
```bash
source .venv/bin/activate
pytest -v
```
All 85 tests cover end-to-end pipeline ingestion, PII scrubbing, RFC 7807 error middleware, dynamic batching, budget governance, and MCP tool execution.

---

## 8. GitHub Actions & Cloud Deployment

### GitHub Actions Scour (`.github/workflows/scheduled_intelligence_scour.yml`)
Runs nightly at 02:00 UTC to execute an automated scour cycle on GitHub's cloud runners.

**Required GitHub Repository Secrets**:
Navigate to **Repo Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions** and add:
* `FIRECRAWL_API_KEY`: Firecrawl API key.
* `XAI_API_KEY`: xAI API key for Grok synthesis.
* `MONGODB_URI`: MongoDB Atlas connection string *(ensure Atlas whitelists `0.0.0.0/0` for runner IPs, or leave blank to run in safe memory fallback)*.

### Render Cloud Blueprint (`render.yaml`)
Deploys the complete production stack to Render:
1. `homepilot-intelligence-service`: FastAPI REST API.
2. `homepilot-intelligence-app`: Node.js frontend/application backend.
3. `homepilot-intelligence-redis`: Coordination queue.
4. `homepilot-market-intelligence-mcp`: 24/7 cloud MCP server for external bots.
5. `homepilot-scheduler-daemon`: Background worker running continuous hourly checks.

---

## 9. Master Documentation Sitemap

For in-depth architectural specifications, see the [`docs/`](docs/) library:
* [docs/README.md](docs/README.md): Master Reading Order & Index.
* [docs/homepilot_market_intelligence_technical_spec.md](docs/homepilot_market_intelligence_technical_spec.md): Schemas and formulas.
* [docs/homepilot_grokbot_desktop_and_mobile_synchronization_spec.md](docs/homepilot_grokbot_desktop_and_mobile_synchronization_spec.md): GrokBot instructions & prompt.
* [docs/homepilot_mcp_and_api_builder_connection_guide.md](docs/homepilot_mcp_and_api_builder_connection_guide.md): MCP vs. REST builder guide.

---

## 10. License & Confidentiality

Internal and proprietary to HomePilot Technologies Ireland. All rights reserved. Zero code or policy dependencies with the standalone Mortgage Calculator Matrix.
