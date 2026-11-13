# HomePilot: MCP Server vs. API Builder Integration Guide

**Engine**: HomePilot Market Intelligence Researcher  
**Status**: Both Built and Operational  
**Date**: November 2026  

---

## 1. Direct Comparison: MCP vs. API to Builder

| Capability | **MCP (Model Context Protocol)** | **API to Builder (OpenAPI Actions)** |
| :--- | :--- | :--- |
| **Best For** | **Mac Desktop Chat Interfaces** (Claude Desktop, Cursor, MCP Clients) | **Mobile Phone Access & Online Bot Builders** (GPT Builder, Web Apps) |
| **Setup Time** | **< 60 seconds** (Paste 4 lines into local config file) | **~3 minutes** (Requires public HTTPS endpoint / tunnel) |
| **Fluidity & Reliability** | **Extremely High**: Direct local process, zero internet latency, zero dropped connections. | **High**: Standard HTTP/JSON REST requests over the web. |
| **Security** | **Maximum**: Pure local inter-process communication (`stdio`). Zero data leaves your machine. | **High**: HTTPS encrypted, token-authenticated. |
| **Mobile Access** | Requires remote SSE tunnel if away from Mac. | **Works Everywhere**: Direct from phone on 5G/Wi-Fi. |

---

## 2. Option 1: The MCP Connection (Recommended for Immediate Desktop Fluidity)

We have built the native MCP server in [`src/mcp_server.py`](file:///Users/samson/Documents/HomePilot's%20projects/External%20Website%20Research%20Tool/src/mcp_server.py).

### The 5 Native Tools Exposed to Your Bot:
1. `get_county_market_benchmarks(county)`: Pulls live PPR median prices, transaction counts, CSO inflation index, and First Home Scheme eligibility gaps.
2. `get_latest_daily_briefing(county)`: Fetches the compiled 07:00 UTC morning intelligence briefing.
3. `search_evidence_pool(query, limit)`: Searches MongoDB for verified quotations, policies, and documents.
4. `submit_knowledge_gap(topic, questions)`: Queues an unanswered question into `research_objectives` for the crawler daemon.
5. `submit_campaign_blueprint(title, format, headline, copy_body, citations)`: Enforces Rule B-02 (2 citations) and stages the asset for Dual Operator Review under Rule B-04.

### How to Connect It in Your Desktop App:
If your desktop app supports MCP (e.g., Claude for Desktop), open its configuration file:
* **Mac Path**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this block under `"mcpServers"`:
```json
{
  "mcpServers": {
    "homepilot_intelligence": {
      "command": "/Users/samson/Documents/HomePilot's projects/External Website Research Tool/.venv/bin/python",
      "args": [
        "/Users/samson/Documents/HomePilot's projects/External Website Research Tool/src/mcp_server.py"
      ],
      "env": {
        "MONGODB_URI": "mongodb://localhost:27017/marketintelligenceresearch",
        "MONGODB_DB_NAME": "marketintelligenceresearch"
      }
    }
  }
}
```

Restart the app. Your bot will now display the native tool hammer/wrench icon. When you ask: *"What are the starter prices in Navan?"*, it automatically calls `get_county_market_benchmarks(county='Meath')` and answers with live ground truth!

---

## 3. Option 2: The API to Builder Connection (For Mobile Phone Access)

If you are using an online Bot Builder (like OpenAI Custom GPTs, Poe API Bot, or a cloud builder) so you can use it on your phone:

1. **Start the API Server**:
   ```bash
   source .venv/bin/activate
   uvicorn src.api.intelligence_api:app --host 0.0.0.0 --port 8000
   ```
2. **Expose with a Secure Public Tunnel**:
   ```bash
   ngrok http 8000
   # Provides public URL: https://xxxx.ngrok-free.app
   ```
3. **In the Bot Builder**:
   - Go to the **"Actions"** or **"Tools"** tab.
   - Enter your schema URL: `https://xxxx.ngrok-free.app/openapi.json` (or import from our OpenAPI spec).
   - The bot builder will automatically configure the actions: `/briefings/latest`, `/market/metrics/{county}`, and `/campaigns/blueprints`.
4. **On Mobile**:
   Open the bot on your iPhone or Android. When you chat with it on the go, it calls your API over HTTPS and gives you the exact same verified research!
