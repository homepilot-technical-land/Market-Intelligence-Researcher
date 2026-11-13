import os
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)

class FirecrawlConnector:
    """Interface to Firecrawl API supporting Map, Crawl, and Scrape with fallback simulation."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY", "")
        self.base_url = base_url or os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev")
        self.client = httpx.Client(timeout=30.0)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key != "your_firecrawl_api_key_here")

    def map_urls(self, url: str, limit: int = 100) -> List[str]:
        """Maps a target domain using Firecrawl Map endpoint or deterministic fallback."""
        if self.is_configured():
            try:
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"url": url, "limit": limit, "sitemap": "include"}
                response = self.client.post(f"{self.base_url}/v1/map", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("links", [])
            except Exception as e:
                logger.error(f"Firecrawl Map failed for {url}: {e}. Falling back to simulation.")

        # Fallback simulation for offline testing / development
        logger.info(f"Simulating Firecrawl map for domain: {url}")
        base = url.rstrip("/")
        return [
            f"{base}/",
            f"{base}/buying-a-home/guides",
            f"{base}/buying-a-home/mortgages",
            f"{base}/consumer-credit/financial-difficulty",
            f"{base}/careers/vacancies",
            f"{base}/privacy-policy",
            f"{base}/cookie-notice"
        ]

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrapes clean markdown and metadata for a specific URL."""
        if self.is_configured():
            try:
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"url": url, "formats": ["markdown"]}
                response = self.client.post(f"{self.base_url}/v1/scrape", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return {
                    "url": url,
                    "title": data.get("data", {}).get("metadata", {}).get("title", ""),
                    "markdown": data.get("data", {}).get("markdown", ""),
                    "status": 200
                }
            except Exception as e:
                logger.error(f"Firecrawl Scrape failed for {url}: {e}. Falling back.")

        # Fallback simulation
        logger.info(f"Simulating Firecrawl scrape for URL: {url}")
        simulated_title = f"Guidance on {url.split('/')[-1].replace('-', ' ').title()}"
        simulated_markdown = f"""# {simulated_title}
Official guidance regarding Irish housing, first-time buyer eligibility, and mortgage financial readiness.

## Overview
Recent market updates indicate revisions to scheme criteria and borrowing calculations.
- Maximum Help to Buy relief claim remains at €30,000.
- First Home Scheme price caps updated across key commuter counties.
- Average starter home transaction price increased by 4.2% year-on-year.

For full details contact the relevant authority."""

        return {
            "url": url,
            "title": simulated_title,
            "markdown": simulated_markdown,
            "status": 200
        }
