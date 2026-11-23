# HomePilot Market Intelligence Researcher & Cognitive Pipeline

Autonomous, multi-source Irish real estate intelligence, statutory policy monitor, and strategic campaign engine designed for the HomePilot Homeownership Operating System.

[![Tests](https://img.shields.io/badge/Tests-85%20Passing-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](requirements.txt)
[![MCP](https://img.shields.io/badge/MCP-Standard%202.3-purple.svg)](src/mcp_server.py)
[![Database](https://img.shields.io/badge/MongoDB-14%20Collections-green.svg)](src/storage/mongo_client.py)
[![FastAPI](https://img.shields.io/badge/API-FastAPI%20RFC%207807-teal.svg)](src/api/intelligence_api.py)
[![GitHub](https://img.shields.io/badge/GitHub-homepilot--technical--land%2FMarket--Intelligence--Researcher-blue.svg)](https://github.com/homepilot-technical-land/Market-Intelligence-Researcher)

---

## 1. Overview & System Purpose

The **HomePilot Market Intelligence Researcher** is an internal intelligence instrument operated by a 2-person leadership team (Product Lead & Legal/Compliance Lead). 

Unlike generic scrapers, it continuously discovers, monitors, sanitizes, scores, and synthesizes empirical Irish property and financial developments across:
1. **Public Macro Data**: Central Statistics Office (CSO PxStat API for HPM05 Property Price Index and NDA02 New Dwellings Completions).
2. **Transaction Registries**: Property Price Register (PPR) county-level starter and mover prices.
3. **Statutory Grant Ceilings**: First Home Scheme (FHS) price caps, Help to Buy (HTB) rules, and Central Bank macroprudential lending limits.
4. **Market Rents**: RTB Rent Index data and buy-vs-rent cash flow comparisons.
5. **Real-Time Discourse**: xAI Grok API (GrokBot) on X and official Reddit OAuth 2.0 discussions across Irish homebuyer communities.
6. **Active Campaign Social Spikes**: Real-time friction monitoring on X matching current active campaign focus areas.

---

## 2. Architecture & Pipeline Lifecycle

The system operates across a 7-stage deterministic funnel backed by 14 Hub-and-Spoke MongoDB collections (with automatic zero-config memory fallback):

```mermaid
flowchart TD
    subgraph S1["1. Multi-Source Ingestion & Discovery"]
        Seeds["35 Approved Irish Sources\n(Gov.ie, Central Bank, Daft, MyHome, CCPC)"]
        FC["Firecrawl API\n(Map / Crawl / Scrape with SSRF Protection)"]
        PublicAPI["Live Macro Connectors\n(CSO PxStat, PPR, RTB Index)"]
        SocialConn["Social Connectors\n(Reddit OAuth 2.0, xAI Grok on X)"]
    end

    subgraph S2["2. Sanitisation & Normalisation"]
        PII["PII Scrubbing Guard\n(Zero-Leakage of Names, Emails, Phone, IBAN)"]
        Norm["Markdown Normaliser & Boilerplate Stripper"]
        PromptGuard["Defensive Prompt Guard\n(Untrusted Web Content Isolation)"]
    end

    subgraph S3["3. Cognitive Scoring & Diff"]
        Tax["12-Category Irish Taxonomy Classifier"]
        Score["6-Dimension Composite Scoring (0–100)"]
        Diff["Semantic Diff Engine (Content Hash Caching)"]
    end

    subgraph S4["4. Campaign Synthesis & Blueprinting"]
        Clust["Theme Clustering Engine\n(Cross-County Benchmark Synthesis)"]
        Batch["Dynamic Regional Batching\n(Campaign-Driven County Focus)"]
        Spike["Regional & Social Spike Alerting\n(Out-of-Focus Anomaly Radar)"]
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
    PII --> Norm --> PromptGuard --> Tax --> Score --> Diff --> Clust --> Batch --> Spike --> Blue --> Grok --> Review
```

---

## 3. Key Capabilities

* **Dynamic Campaign-Driven Regional Batching**: Automatically aligns the 07:00 UTC morning intelligence brief to the active marketing campaign's focus counties (e.g. Meath, Kildare, Wicklow).
* **Out-of-Focus Regional Anomaly Radar**: Detects regulatory shifts, planning refusals, or price surges in non-focus counties and flags them as priority alerts.
* **Active Campaign Social Spikes on X**: Real-time buyer conversation radar checking active campaign themes on X for emerging friction or spikes.
* **Multi-Platform Social Discourse Ingestion**: 
  - Official Reddit OAuth 2.0 integration for extracting full discussion posts and comment trees.
  - Social thread extraction covering Reddit, X (Twitter), Facebook, and Instagram.
  - Persona segmentation for both First-Time Buyers (FTB) and Second-Time Buyers (STB / home movers).
* **Native Model Context Protocol (MCP) Server**: Provides external agents (GrokBot, Claude Desktop, Cursor) with native tools to query live property data, scrape URLs, and submit knowledge gaps over `stdio`, `streamable-http`, or `sse`.
* **FastAPI Gateway with Built-in Chat**: REST API with RFC 7807 problem details, direct `/mcp` mount, and responsive mobile/desktop `/chat` UI.
* **Hardened Security & Privacy**:
  - PII Scrubbing for emails, phone numbers, and IBANs.
  - Server-Side Request Forgery (SSRF) protection blocking private RFC 1918 IPs and cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`).
  - Defensive prompt injection encapsulation (`<untrusted_web_content>`).
  - Internal API key authentication (`X-HomePilot-Key`).
* **Budget & Quota Governance**: Hard limits guarding monthly external API costs (€14 Firecrawl ceiling, €25 xAI Grok ceiling) with automatic rate limiting and telemetry tracking.
* **Hermetic Resilience & Zero-Config CI/CD**: Safe startup and in-memory fallback ensure the system runs seamlessly even if MongoDB or external credentials are temporarily offline.

---

## 4. Repository Structure

```
.
├── config/
│   ├── sources_registry.json         # 35 approved Irish seed sources with cadences & tiers
│   └── budget_and_quota_policy.json  # Hard spending limits & token cost weights
├── docs/                             # Complete 31-document architectural archive
├── src/
│   ├── api/                          # FastAPI REST service with RFC 7807 problem details & /chat UI
│   ├── connectors/                   # Firecrawl, CSO, PPR, RTB, and Reddit OAuth connectors
│   ├── coordination/                 # Budget governance tracker and Redis queue manager
│   ├── generators/                   # Asset blueprint builder (Rule B-02 citation enforcement)
│   ├── intelligence/                 # Taxonomy, scoring, Grok service, theme clustering, briefing
│   ├── models/                       # Pydantic schemas across all 14 core domain models
│   ├── normalisation/                # Document normaliser and PII scrubbing engine
│   ├── pipeline/                     # 7-stage pipeline orchestrator (MarketIntelligencePipeline)
│   ├── scheduling/                   # 24/7 background daemon (briefings, cadence, gap processor)
│   ├── storage/                      # Unified MongoDB repository with safe memory fallback
│   └── mcp_server.py                 # Multi-transport MCP Server (stdio, streamable-http, sse)
├── tests/                            # Comprehensive hermetic test suite (85 tests passing)
├── .github/workflows/
│   ├── ci.yml                        # Automated pull request and push test runner
│   └── scheduled_intelligence_scour.yml # Nightly 02:00 UTC automated intelligence scour
├── cli.py                            # Operator CLI (daemon, review, clustering, research)
├── render.yaml                       # Multi-service Render cloud deployment blueprint
├── requirements.txt                  # Python dependencies
└── run_mcp_tunnel.sh                 # Cloudflare tunnel runner for GrokBot MCP access
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
git clone https://github.com/homepilot-technical-land/Market-Intelligence-Researcher.git
cd Market-Intelligence-Researcher

# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```
Key configuration parameters:
```ini
# External Cognitive & Crawling APIs
FIRECRAWL_API_KEY=fc-...
XAI_API_KEY=xai-...
GROK_MODEL=grok-4.20-0309-non-reasoning

# Reddit API (Optional for full thread & comment tree extraction)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=HomePilot-Market-Intelligence/1.0

# Database & Cache (Optional - falls back to memory repository if offline)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/marketintelligenceresearch
MONGODB_DB_NAME=marketintelligenceresearch
REDIS_URL=redis://localhost:6379

# Internal Service Security
HOMEPILOT_INTERNAL_API_KEY=hp_sec_change_me_in_production

# Service Configuration
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
# Streamable HTTP mode (starts on port 8001, mountable for GrokBot & web agents)
python src/mcp_server.py --transport streamable-http --port 8001

# Stdio mode (for local Claude Desktop / Cursor CLI pipes)
python src/mcp_server.py --transport stdio

# Cloudflare Tunnel for live GrokBot mobile/web access
./run_mcp_tunnel.sh
```

### 4. Connect MCP to Claude Desktop
Add this entry to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "homepilot_intelligence": {
      "command": "/absolute/path/to/Market-Intelligence-Researcher/.venv/bin/python",
      "args": [
        "/absolute/path/to/Market-Intelligence-Researcher/src/mcp_server.py",
        "--transport",
        "stdio"
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
* **Interactive API Documentation (Swagger UI)**: `http://localhost:8000/docs`
* **Built-in GrokBot Chat UI**: `http://localhost:8000/chat`
* **Mounted MCP Endpoint**: `http://localhost:8000/mcp`
* **Health Check**: `http://localhost:8000/health`

### 6. Available MCP Tools
External AI assistants (GrokBot, Claude Desktop) have access to 14 native tools:
| Tool Name | Description |
|---|---|
| `get_county_market_benchmarks` | PPR starter/mover prices, CSO inflation rates, and FHS caps for any Irish county. |
| `get_latest_daily_briefing` | Latest compiled daily morning intelligence brief for a county. |
| `search_evidence_pool` | Search indexed evidence snippets by topic or scheme. |
| `submit_knowledge_gap` | Queue an empirical knowledge gap for crawler ingestion. |
| `submit_campaign_blueprint` | Validate and store campaign blueprints (enforces Rule B-02 citation gate). |
| `ask_research_engine` | Retrieve factual context with engine guidance for questions. |
| `scrape_web_url` | Extract clean markdown from any URL via Firecrawl. |
| `search_web_sources` | Search-then-scrape Irish property and financial sources. |
| `extract_social_thread` | Extract discussions across Reddit, X, Facebook, and Instagram. |
| `synthesize_x_discourse` | Grok synthesis of live buyer discourse on X (FTB, STB, or both). |
| `get_active_campaign_focus` | Inspect the active campaign's target counties and core themes. |
| `set_active_campaign_focus` | Update regional focus counties and themes for batching. |
| `check_regional_spikes` | Detect anomalies and price spikes outside current focus counties. |
| `check_campaign_social_spikes` | Detect friction spikes on X matching active campaign themes. |

### 7. Operator Review CLI (Rule B-04 Dual Signoff)
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
All **85 tests** pass hermetically across:
- Pipeline ingestion and source discovery
- PII scrubbing and SSRF network guards
- RFC 7807 problem details error handling
- Campaign-driven dynamic regional batching and out-of-focus anomaly detection
- Reddit OAuth connector and anti-bot fallbacks
- Model Context Protocol (MCP) tool execution and schema validation

---

## 8. GitHub Actions & Cloud Deployment

### GitHub Actions Scour (`.github/workflows/scheduled_intelligence_scour.yml`)
Runs nightly at 02:00 UTC to execute an automated scour cycle on GitHub cloud runners. Supports on-demand manual dispatch via the GitHub Actions tab.

**Required GitHub Repository Secrets**:
Navigate to **Repo Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions** and configure:
* `FIRECRAWL_API_KEY`: Firecrawl API key.
* `XAI_API_KEY`: xAI API key for Grok synthesis.
* `MONGODB_URI`: MongoDB Atlas connection string *(safe fallback to memory if unconfigured)*.
* `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`: *(Optional)* for Reddit discussions.

### Render Cloud Blueprint (`render.yaml`)
Deploys the complete production stack to Render:
1. `homepilot-intelligence-service`: FastAPI REST API with mounted MCP and Chat UI.
2. `homepilot-intelligence-app`: Companion Node.js application service.
3. `homepilot-intelligence-redis`: Coordination queue.
4. `homepilot-market-intelligence-mcp`: 24/7 cloud MCP server for external bots.
5. `homepilot-scheduler-daemon`: Background worker running continuous hourly checks.

---

## 9. Master Documentation Sitemap

For in-depth architectural specifications, see the [`docs/`](docs/) library:
* [docs/README.md](docs/README.md): Master Reading Order & Index across all 31 design documents.
* [docs/homepilot_market_intelligence_technical_spec.md](docs/homepilot_market_intelligence_technical_spec.md): Schemas and formulas.
* [docs/homepilot_grokbot_desktop_and_mobile_synchronization_spec.md](docs/homepilot_grokbot_desktop_and_mobile_synchronization_spec.md): GrokBot instructions & prompt.
* [docs/homepilot_mcp_and_api_builder_connection_guide.md](docs/homepilot_mcp_and_api_builder_connection_guide.md): MCP vs. REST builder guide.

---

## 10. License & Confidentiality

Internal and proprietary to HomePilot Technologies Ireland. All rights reserved. Zero code or policy dependencies with the standalone Mortgage Calculator Matrix.
