import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import httpx

logger = logging.getLogger(__name__)

class PostHogTelemetry:
    """Operational Observability & Metrics Engine via PostHog.
    
    Tracks pipeline health, token economy, crawl credit consumption,
    and agent execution lifecycle without transmitting sensitive customer data.
    MongoDB remains the primary source of truth; PostHog is used purely for operational telemetry.
    """

    ALLOWED_EVENTS = [
        "source.crawl.completed",
        "source.page.discovered",
        "document.relevance.scored",
        "document.change.detected",
        "research.objective.completed",
        "source.recommendation.created",
        "campaign.opportunity.generated",
        "grok.api.cost.recorded",
        "crawl.credit.consumed",
        "agent.execution.failed"
    ]

    def __init__(self, api_key: Optional[str] = None, host: Optional[str] = None):
        self.api_key = api_key or os.getenv("POSTHOG_API_KEY", "")
        self.host = host or os.getenv("POSTHOG_HOST", "https://eu.i.posthog.com")
        self.client = httpx.Client(timeout=10.0)
        self.distinct_id = "homepilot_intel_operator"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_posthog_api_key_here")

    def capture(self, event_name: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """Captures an operational metric event with strict privacy guards."""
        if event_name not in self.ALLOWED_EVENTS:
            logger.warning(f"Unregistered PostHog event '{event_name}' ignored.")
            return False

        props = properties or {}
        # Enforce metadata-only sanitization: strip any PII or customer financial records
        sanitized_props = {
            k: v for k, v in props.items() 
            if not any(pii_key in k.lower() for pii_key in ["email", "password", "iban", "ssn", "personal", "customer_name"])
        }
        sanitized_props["$lib"] = "homepilot-internal-telemetry"
        sanitized_props["timestamp"] = datetime.now(timezone.utc).isoformat()
        sanitized_props["environment"] = os.getenv("ENVIRONMENT", "development")

        if self.is_configured():
            try:
                payload = {
                    "api_key": self.api_key,
                    "event": event_name,
                    "distinct_id": self.distinct_id,
                    "properties": sanitized_props
                }
                res = self.client.post(f"{self.host.rstrip('/')}/capture/", json=payload)
                res.raise_for_status()
                return True
            except Exception as e:
                logger.warning(f"PostHog telemetry capture failed: {e}. Non-blocking.")
                return False

        logger.debug(f"[PostHog Telemetry Simulation] Captured: {event_name} | Props: {sanitized_props}")
        return True
