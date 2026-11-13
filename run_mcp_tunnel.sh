#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo " Starting HomePilot Market Intelligence MCP Server & Tunnel"
echo "=========================================================="

# Ensure cloudflared is accessible
export PATH="$HOME/.local/bin:$PATH"

# Kill any existing server on port 8001
lsof -ti :8001 | xargs kill -9 2>/dev/null || true

# Start MCP Server in background
echo "[1/2] Starting MCP Server on port 8001..."
.venv/bin/python src/mcp_server.py --transport streamable-http --port 8001 &
SERVER_PID=$!

# Trap exit to kill server on Ctrl+C
cleanup() {
    echo ""
    echo "Stopping MCP Server (PID $SERVER_PID) and Cloudflare Tunnel..."
    kill $SERVER_PID 2>/dev/null || true
    pkill -f "cloudflared tunnel --url http://localhost:8001" 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

sleep 2

# Start Cloudflare Tunnel
echo "[2/2] Launching Cloudflare Tunnel..."
cloudflared tunnel --url http://localhost:8001
