/**
 * HomePilot Market Intelligence Application Service (Node.js)
 * Responsible for API gateway, review dashboard integration, and workflow orchestration.
 */

const http = require('http');

const PORT = process.env.APPLICATION_SERVICE_PORT || 3000;
const PYTHON_INTELLIGENCE_URL = process.env.PYTHON_INTELLIGENCE_URL || 'http://localhost:8000';

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');

  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      status: 'healthy',
      service: 'homepilot_application_service',
      python_backend_url: PYTHON_INTELLIGENCE_URL,
      timestamp: new Date().toISOString()
    }));
  } else if (req.url === '/api/review/queue' && req.method === 'GET') {
    res.writeHead(200);
    res.end(JSON.stringify({
      pending_approvals: [],
      candidate_sources_pending: 6,
      message: 'Human review queue operational'
    }));
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Endpoint not found' }));
  }
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`[HomePilot Node.js Application Service] Running on port ${PORT}`);
  });
}

module.exports = server;
