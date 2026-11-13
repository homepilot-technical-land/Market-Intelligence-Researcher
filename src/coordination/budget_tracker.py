import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from src.storage.repository import IntelligenceRepository
from src.observability.posthog_client import PostHogTelemetry

logger = logging.getLogger(__name__)

class MonthlyBudgetBurn(BaseModel):
    billing_month: str # e.g. "2026-11"
    firecrawl_credits_used: int = 0
    firecrawl_credit_limit: int = 5000
    xai_cost_usd: float = 0.0
    xai_budget_limit_usd: float = 27.0
    pages_processed_free_hash: int = 0
    estimated_dollars_saved_by_cache: float = 0.0
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BudgetGovernanceTracker:
    """Real-Time Budget & Quota Governance Tracker.
    
    Enforces hard constraints to keep monthly operating spend strictly within
    €14 for Firecrawl (5,000 pages) and €25 for xAI Grok (~$27 USD), with
    database and infrastructure costs remaining below €10.
    """

    def __init__(
        self,
        config_path: str = "config/budget_and_quota_policy.json",
        state_file: Optional[str] = None,
        repository: Optional[IntelligenceRepository] = None,
        telemetry: Optional[PostHogTelemetry] = None
    ):
        self.config_path = config_path
        self.state_file = state_file or os.getenv("BUDGET_STATE_FILE")
        self.repo = repository or IntelligenceRepository()
        self.telemetry = telemetry or PostHogTelemetry()
        self.policy = self._load_policy()
        self._local_burn_store: Dict[str, Dict[str, Any]] = self._load_burn_state()

    def _load_burn_state(self) -> Dict[str, Dict[str, Any]]:
        if self.state_file and os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_burn_state(self):
        if not self.state_file:
            return
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            serializable = {}
            for m, data in self._local_burn_store.items():
                serializable[m] = {
                    k: (v.isoformat() if hasattr(v, "isoformat") else v)
                    for k, v in data.items()
                }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist local budget burn state: {e}")

    def _load_policy(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "firecrawl": {"monthly_credit_limit": 5000, "warning_threshold_credits": 4500},
            "xai_grok": {"monthly_budget_usd": 27.00, "warning_threshold_usd": 22.00}
        }

    def _current_month(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def get_current_burn(self) -> MonthlyBudgetBurn:
        month = self._current_month()
        limit_fc = self.policy.get("firecrawl", {}).get("monthly_credit_limit", 5000)
        limit_xai = self.policy.get("xai_grok", {}).get("monthly_budget_usd", 27.0)

        # Check repository or in-memory
        data = self._local_burn_store.get(month)
        if not data:
            data = {
                "billing_month": month,
                "firecrawl_credits_used": 0,
                "firecrawl_credit_limit": limit_fc,
                "xai_cost_usd": 0.0,
                "xai_budget_limit_usd": limit_xai,
                "pages_processed_free_hash": 0,
                "estimated_dollars_saved_by_cache": 0.0,
                "last_updated_at": datetime.now(timezone.utc)
            }
            self._local_burn_store[month] = data
        return MonthlyBudgetBurn(**data)

    def can_consume_firecrawl(self, credits: int = 1) -> Tuple[bool, str]:
        """Checks if Firecrawl quota permits scraping without exceeding 5,000 credits."""
        burn = self.get_current_burn()
        limit = burn.firecrawl_credit_limit
        if burn.firecrawl_credits_used + credits > limit:
            msg = f"Firecrawl quota exhausted: {burn.firecrawl_credits_used}/{limit} credits used."
            logger.warning(msg)
            return False, msg

        warning_threshold = self.policy.get("firecrawl", {}).get("warning_threshold_credits", 4500)
        if burn.firecrawl_credits_used + credits >= warning_threshold:
            logger.info(f"Firecrawl nearing limit: {burn.firecrawl_credits_used + credits}/{limit} credits.")

        return True, "Quota approved"

    def can_consume_xai(self, estimated_cost_usd: float = 0.007) -> Tuple[bool, str]:
        """Checks if xAI token spend permits inference without exceeding €25 (~$27 USD)."""
        burn = self.get_current_burn()
        limit = burn.xai_budget_limit_usd
        if burn.xai_cost_usd + estimated_cost_usd > limit:
            msg = f"xAI API monthly budget reached: ${burn.xai_cost_usd:.2f}/${limit:.2f} USD."
            logger.warning(msg)
            return False, msg

        warning_threshold = self.policy.get("xai_grok", {}).get("warning_threshold_usd", 22.0)
        if burn.xai_cost_usd + estimated_cost_usd >= warning_threshold:
            logger.info(f"xAI API approaching €25 ceiling: ${burn.xai_cost_usd + estimated_cost_usd:.2f} spent.")

        return True, "Budget approved"

    def record_firecrawl_consumption(self, credits: int = 1, endpoint: str = "scrape", source_id: str = ""):
        month = self._current_month()
        burn = self.get_current_burn()
        burn.firecrawl_credits_used += credits
        burn.last_updated_at = datetime.now(timezone.utc)
        self._local_burn_store[month] = burn.model_dump()
        self._save_burn_state()

        self.telemetry.capture("crawl.credit.consumed", {
            "source_id": source_id,
            "credits_used": credits,
            "endpoint": endpoint,
            "total_credits_used_month": burn.firecrawl_credits_used,
            "quota_remaining": burn.firecrawl_credit_limit - burn.firecrawl_credits_used
        })

    def record_xai_consumption(self, cost_usd: float, tokens_used: int = 0, doc_id: str = ""):
        month = self._current_month()
        burn = self.get_current_burn()
        burn.xai_cost_usd = round(burn.xai_cost_usd + cost_usd, 4)
        burn.last_updated_at = datetime.now(timezone.utc)
        self._local_burn_store[month] = burn.model_dump()
        self._save_burn_state()

        self.telemetry.capture("grok.api.cost.recorded", {
            "doc_id": doc_id,
            "cost_usd": cost_usd,
            "tokens_used": tokens_used,
            "total_xai_spent_month": burn.xai_cost_usd,
            "budget_remaining_usd": round(burn.xai_budget_limit_usd - burn.xai_cost_usd, 2)
        })

    def record_cache_bypass(self, pages: int = 1):
        """Records financial savings whenever SHA-256 idempotency prevents an LLM invocation."""
        month = self._current_month()
        burn = self.get_current_burn()
        burn.pages_processed_free_hash += pages
        # Every bypassed page saves ~1,900 tokens = ~$0.007 USD
        burn.estimated_dollars_saved_by_cache = round(burn.estimated_dollars_saved_by_cache + (pages * 0.007), 3)
        burn.last_updated_at = datetime.now(timezone.utc)
        self._local_burn_store[month] = burn.model_dump()
        self._save_burn_state()
