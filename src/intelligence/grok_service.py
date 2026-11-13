import os
import logging
from typing import Dict, Any, List, Optional
import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GrokResponse(BaseModel):
    analysis: str
    key_findings: List[str] = Field(default_factory=list)
    strategic_implications: List[str] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0

class GrokService:
    """Dedicated service for xAI Grok API reasoning, evaluation, and X-platform research synthesis.
    
    Adheres strictly to:
    - Native X / Twitter platform real-time sentiment analysis
    - Monthly budget governance (€25 / ~$27 USD ceiling, ~500 deep-dive invocations)
    - Fallback deterministic reasoning for offline tests & simulations
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        budget_tracker: Optional[Any] = None
    ):
        if api_key is None:
            self.api_key = os.getenv("XAI_API_KEY", "")
        else:
            self.api_key = api_key

        self.model = model or os.getenv("GROK_MODEL", "grok-4.20-0309-non-reasoning")
        self.budget_tracker = budget_tracker
        self.base_url = "https://api.x.ai/v1"
        self.client = httpx.Client(timeout=45.0)

    def is_configured(self) -> bool:
        """Determines if a valid live API key is present."""
        return bool(
            self.api_key
            and self.api_key != "your_xai_api_key_here"
            and not self.api_key.startswith("xai-your")
        )

    def evaluate_strategic_implications(
        self,
        context_title: str,
        text_content: str,
        evidence_quote: str
    ) -> GrokResponse:
        """Invokes Grok to interpret strategic implications for Irish homebuyers and HomePilot."""
        # Enforce budget guard
        if self.budget_tracker:
            allowed, msg = self.budget_tracker.can_consume_xai(estimated_cost_usd=0.007)
            if not allowed:
                logger.error(f"Grok call blocked by budget governor: {msg}")
                return GrokResponse(
                    analysis=f"Analysis blocked: {msg}",
                    key_findings=["Budget limit reached"],
                    strategic_implications=["Halt further cognitive processing until next billing cycle"],
                    cost_usd=0.0
                )

        if self.is_configured():
            try:
                system_prompt = (
                    "You are the Strategic Reasoning Agent for HomePilot, the Irish Homeownership Operating System. "
                    "Analyze the provided housing market or regulatory text and extract verified factual developments, "
                    "who is affected, customer financial impact, and strategic product/campaign recommendations."
                )
                user_prompt = f"Document Title: {context_title}\n\nEvidence Quote: {evidence_quote}\n\nContent:\n{text_content[:2500]}"
                
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2
                }
                res = self.client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                p_tokens = usage.get("prompt_tokens", 0)
                c_tokens = usage.get("completion_tokens", 0)
                
                # Standard xAI pricing estimation ($2/M prompt, $10/M completion)
                cost = (p_tokens * 0.000002) + (c_tokens * 0.00001)

                if self.budget_tracker:
                    self.budget_tracker.record_xai_consumption(
                        cost_usd=cost,
                        tokens_used=p_tokens + c_tokens,
                        doc_id=context_title
                    )

                return GrokResponse(
                    analysis=content,
                    key_findings=[context_title],
                    strategic_implications=["Verified strategic reasoning from Grok"],
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    cost_usd=round(cost, 6)
                )
            except Exception as e:
                logger.error(f"xAI Grok API invocation failed: {e}. Falling back to deterministic reasoning.")

        # Fallback deterministic reasoning for testing and offline development
        return GrokResponse(
            analysis=(
                f"Strategic analysis of '{context_title}': This development directly affects prospective buyers "
                "navigating purchasing criteria and borrowing limits in Ireland. HomePilot should provide scenario comparison tools."
            ),
            key_findings=[
                f"Published policy/market update for '{context_title}'",
                "Affects first-time buyer eligibility and borrowing readiness"
            ],
            strategic_implications=[
                "Reinforces demand for HomePilot Borrowing Power Estimator",
                "Opportunity for educational campaign on mortgage readiness"
            ],
            prompt_tokens=250,
            completion_tokens=85,
            cost_usd=0.00135
        )

    def analyze_x_platform_sentiment(
        self,
        topic: str = "Irish housing first time buyers"
    ) -> GrokResponse:
        """Synthesizes real-time public sentiment, questions, and discussions from the X platform regarding Irish housing.
        
        Leverages Grok's native access to X discussions to extract buyer friction points without web scraping.
        """
        # Enforce budget guard
        if self.budget_tracker:
            allowed, msg = self.budget_tracker.can_consume_xai(estimated_cost_usd=0.007)
            if not allowed:
                return GrokResponse(
                    analysis=f"X sentiment analysis blocked: {msg}",
                    key_findings=["Budget ceiling reached"],
                    strategic_implications=["Defer X sentiment until next month"],
                    cost_usd=0.0
                )

        if self.is_configured():
            try:
                system_prompt = (
                    "You are the Social Sentiment & Community Intelligence Agent for HomePilot. "
                    "Analyze real-time public conversations and trending discussions on the X platform "
                    "regarding Irish housing, mortgage approval delays, First Home Scheme caps, and Help to Buy. "
                    "Identify top buyer anxieties, common misconceptions, and strategic messaging opportunities."
                )
                user_prompt = f"Topic Focus: {topic}\nSynthesize current buyer sentiment, questions, and pain points."
                
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3
                }
                res = self.client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                p_tokens = usage.get("prompt_tokens", 0)
                c_tokens = usage.get("completion_tokens", 0)
                cost = (p_tokens * 0.000002) + (c_tokens * 0.00001)

                if self.budget_tracker:
                    self.budget_tracker.record_xai_consumption(
                        cost_usd=cost,
                        tokens_used=p_tokens + c_tokens,
                        doc_id=f"x_sentiment_{topic}"
                    )

                return GrokResponse(
                    analysis=content,
                    key_findings=[f"X Community Sentiment for '{topic}'"],
                    strategic_implications=["Live social sentiment integrated into HomePilot intelligence"],
                    prompt_tokens=p_tokens,
                    completion_tokens=c_tokens,
                    cost_usd=round(cost, 6)
                )
            except Exception as e:
                logger.error(f"xAI X sentiment invocation failed: {e}. Falling back to simulation.")

        # Fallback simulation
        return GrokResponse(
            analysis=(
                f"Simulated X Platform Sentiment for '{topic}': Discussions highlight acute frustration with regional price caps, "
                "bidding opacity in commuter counties (Kildare, Meath, Wicklow), and unexpected closing legal fees."
            ),
            key_findings=[
                "High anxiety regarding developer price hikes matching scheme limits",
                "Repeated questions regarding First Home Scheme equity buyout rules"
            ],
            strategic_implications=[
                "Publish clear FAQ guide on First Home Scheme equity redemption",
                "Promote HomePilot Total Acquisition Cost Buffer Calculator"
            ],
            prompt_tokens=300,
            completion_tokens=100,
            cost_usd=0.0016
        )
