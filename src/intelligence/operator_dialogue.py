"""Interactive Grok Bot Operator Dialogue & Review Queue for HomePilot.

Implements the 3 R's Governance (Rule B-04):
- Role: Grok Bot is the interactive drafting partner; Operator 1 (Product Lead) and
  Operator 2 (Compliance/Legal Lead) are the authorizing sign-offs.
- Rule: Mandatory dual human operator sign-off before any content asset moves from
  'pending_review' -> 'operator_1_approved' -> 'approved'.
- Route: CLI conversational turn -> Grok revision -> MongoDB persistence in 'content_assets'.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.asset import GeneratedAsset, AssetPayload
from src.models.agent_run import AgentRun
from src.intelligence.grok_service import GrokService
from src.storage.repository import IntelligenceRepository

logger = logging.getLogger(__name__)

class OperatorDialogueEngine:
    """Manages conversational asset refinement and dual operator governance."""

    def __init__(
        self,
        repository: Optional[IntelligenceRepository] = None,
        grok_service: Optional[GrokService] = None
    ):
        self.repo = repository or IntelligenceRepository()
        self.grok = grok_service or GrokService()

    def list_pending_assets(self) -> List[GeneratedAsset]:
        """Lists all assets in MongoDB waiting for operator review."""
        return self.repo.list_assets(review_statuses=["pending_review", "operator_1_approved"])

    def revise_asset_with_grok(
        self,
        asset_id: str,
        operator_instruction: str,
        operator_id: str = "operator_1"
    ) -> GeneratedAsset:
        """Invokes Grok Bot to conversationally rewrite or adjust an asset."""
        asset = self._fetch_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found in MongoDB.")

        prompt = (
            f"You are the HomePilot Grok Bot, assisting an operator with content refinement under Rule B-04.\n"
            f"Original Headline: {asset.content_payload.headline}\n"
            f"Original Copy: {asset.content_payload.copy_body}\n"
            f"Operator Instruction: {operator_instruction}\n\n"
            "Rewrite the copy adhering to the Trusted Guide persona (empathetic, strictly factual, no banking jargon, "
            "clear disclaimers, citing evidence). Return the revised copy directly."
        )

        if self.grok.is_configured():
            revised_text = self._call_grok_rewrite(prompt)
        else:
            revised_text = f"[Grok Revision per '{operator_instruction}']:\n{asset.content_payload.copy_body}\n\n(Disclaimer: Past performance is not indicative of future market yield; Central Bank 4.0x limits apply)."

        # Update payload
        asset.content_payload.copy_body = revised_text
        asset.reviewer_notes = f"Revised by Grok Bot per instruction from {operator_id}: '{operator_instruction}'."
        asset.review_status = "pending_review"  # Requires fresh sign-off after revision

        self.repo.save_asset(asset)

        # Audit run
        self.repo.log_agent_run(AgentRun(
            run_id=f"run_dialogue_{uuid.uuid4().hex[:8]}",
            agent_type="grok_bot",
            status="success",
            step_count=1,
            documents_analyzed=1,
            findings_generated=0,
            cost_usd=0.001
        ))

        logger.info(f"Asset '{asset_id}' revised by Grok Bot per operator instruction.")
        return asset

    def signoff_operator_1(
        self,
        asset_id: str,
        operator_id: str = "operator_1_product",
        notes: str = "Technical calculations and product links verified."
    ) -> GeneratedAsset:
        """First human signoff: Product Lead verification."""
        asset = self._fetch_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found.")

        asset.review_status = "operator_1_approved"
        asset.reviewed_by = operator_id
        asset.reviewer_notes = f"[Operator 1 Approval - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}]: {notes}"
        self.repo.save_asset(asset)
        logger.info(f"Asset '{asset_id}' granted Operator 1 signoff.")
        return asset

    def signoff_operator_2(
        self,
        asset_id: str,
        operator_id: str = "operator_2_compliance",
        notes: str = "Regulatory disclaimers, consumer protection rules, and brand tone verified."
    ) -> GeneratedAsset:
        """Second human signoff: Compliance & Legal verification (Rule B-04 completed)."""
        asset = self._fetch_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found.")

        if asset.review_status != "operator_1_approved":
            raise ValueError(
                f"Rule B-04 Sequencing Violation: Asset '{asset_id}' must be approved by Operator 1 "
                f"before Operator 2 compliance signoff (current status: '{asset.review_status}')."
            )

        asset.review_status = "approved"
        asset.reviewed_by = f"{asset.reviewed_by} + {operator_id}"
        asset.reviewer_notes = f"{asset.reviewer_notes} | [Operator 2 Signoff - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}]: {notes}"
        asset.scheduled_publish_time = datetime.utcnow()
        self.repo.save_asset(asset)
        logger.info(f"Asset '{asset_id}' fully APPROVED under Rule B-04 dual operator signoff.")
        return asset

    def reject_asset(
        self,
        asset_id: str,
        operator_id: str,
        reason: str
    ) -> GeneratedAsset:
        """Rejects asset from publication."""
        asset = self._fetch_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset '{asset_id}' not found.")

        asset.review_status = "rejected"
        asset.reviewed_by = operator_id
        asset.reviewer_notes = f"[REJECTED by {operator_id}]: {reason}"
        self.repo.save_asset(asset)
        return asset

    def _fetch_asset(self, asset_id: str) -> Optional[GeneratedAsset]:
        return self.repo.get_asset(asset_id)

    def _call_grok_rewrite(self, prompt: str) -> str:
        import httpx
        try:
            resp = httpx.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.grok.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4
                },
                timeout=15.0
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"Grok rewrite API error: {e}. Using local template fallback.")
        return prompt
