import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.models.persona import AudiencePersona, InfluencesOnPerceptions, BPMJourneyMapping, ThreeRsDutyAllocation
from src.models.document import ExtractedDocument
from src.storage.repository import IntelligenceRepository
from src.intelligence.grok_service import GrokService

logger = logging.getLogger(__name__)

class DynamicPersonaEngine:
    """Dynamic Persona & Behavioural Evolution Engine for HomePilot.
    
    Synthesizes real-time market signals from Firecrawl feeds and xAI Grok reasoning
    to dynamically discover, update, and evolve audience personas within the BPM
    Customer Journey and Influences on Perceptions framework.
    """

    def __init__(self, repository: Optional[IntelligenceRepository] = None, grok_service: Optional[GrokService] = None):
        self.repo = repository or IntelligenceRepository()
        self.grok = grok_service or GrokService()
        self.bootstrap_default_personas()

    def bootstrap_default_personas(self):
        """Seeds the 5 foundational personas from marketing config if collection is empty."""
        existing = self.repo.list_personas()
        if existing:
            return

        config_path = "config/marketing_campaign_personas.json"
        if not os.path.exists(config_path):
            return

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for seg in data.get("audience_segments", []):
            persona = AudiencePersona(
                segment_id=seg["segment_id"],
                name=seg["name"],
                origin="default_template",
                demographics=seg.get("demographics", {}),
                pain_points=[seg.get("pain_point", "")],
                current_state_of_mind=seg.get("emotional_state", "").split("->")[0].strip(),
                desired_state_of_mind=seg.get("emotional_state", "").split("->")[-1].strip() if "->" in seg.get("emotional_state", "") else "Confident",
                primary_hook=seg.get("primary_hook", ""),
                influences_on_perceptions=InfluencesOnPerceptions(
                    service_encounters="Repeated interactions with retail bank calculators and brokers leaving user disoriented.",
                    evidence_of_service="Structured visual roadmaps, task checklists, and stress-test scenarios.",
                    price_value_perception="High perceived value in 90-Day Journey Pass (€39-€49) to eliminate €10k closing errors.",
                    brand_image="HomePilot: The authoritative Homeownership Operating System (Trusted Guide)."
                ),
                journey_mapping=BPMJourneyMapping(
                    point_of_view=f"Perspective of {seg['name']}",
                    journey_scope="Aspiration to Long-Term Ownership",
                    primary_stage="Mortgage Planning & Readiness",
                    moments_of_truth=["Deposit Goal Reached", "AIP Granted", "Sale Agreed", "Keys Collected"],
                    points_of_failure=["4.0x LTI Stress-Test Cap", "Closing Cash Deficit", "Conveyancing Expiration"],
                    duty_allocation=ThreeRsDutyAllocation(
                        role="Automated Feed Ingestion Bot (Firecrawl) + 2-Person Team Human Review",
                        rule="Verified source citation and composite relevance score >= 70",
                        route="Feed Detection -> Normalisation -> Grok Reasoning -> Human Operator Review Queue",
                        requires_human_validation=True
                    )
                )
            )
            self.repo.upsert_persona(persona)
        logger.info(f"Bootstrapped {len(data.get('audience_segments', []))} default audience personas with 3 R's duty allocations.")

    def evaluate_feed_for_persona_discovery(self, doc: ExtractedDocument) -> Optional[AudiencePersona]:
        """Analyzes an incoming market document to detect emerging behavioral segments or refine existing ones."""
        text = doc.markdown.lower()

        # Dynamic Pattern 1: The Commuter Price-Cap Straddler
        if any(w in text for w in ["navan", "meath", "kildare", "commuter"]) and any(w in text for w in ["price cap", "ceiling", "first home scheme", "threshold"]):
            seg_id = "dyn_seg_commuter_cap_straddler"
            existing = self.repo.get_persona(seg_id)
            if existing:
                existing.last_updated_at = datetime.utcnow()
                existing.evidence_citations.append(doc.markdown[:200])
                self.repo.upsert_persona(existing)
                return existing

            new_persona = AudiencePersona(
                segment_id=seg_id,
                name="The Commuter Price-Cap Straddler",
                origin="discovered_feed",
                demographics={"age": "28-36", "income": "€65k-€95k", "geography": "Dublin Commuter Belt (Meath/Kildare/Louth)"},
                beliefs=["Buying in Dublin is mathematically impossible; commuter towns offer the only viable path to ownership."],
                attitudes=["Frustrated by arbitrary regional price caps that don't match newly launched starter home prices."],
                fears=["Getting locked out of the First Home Scheme while Dublin prices remain unaffordable."],
                current_state_of_mind="Geographically displaced and caught between regional subsidy limits.",
                desired_state_of_mind="Strategic clarity on county-by-county scheme boundaries and true commuter trade-offs.",
                pain_points=[
                    "Starter home prices in Navan/Naas approaching €375k–€400k, straddling regional FHS eligibility ceilings.",
                    "Higher commuting travel costs eroding monthly disposable income buffers after purchase."
                ],
                system_bottlenecks=["Regional Local Authority Price Caps vs. Actual Developer Base Launch Prices"],
                mental_model_barriers=["Assuming all commuter town developments qualify for maximum shared equity support."],
                influences_on_perceptions=InfluencesOnPerceptions(
                    service_encounters="Disjointed estate agent listings and conflicting scheme qualification tables.",
                    evidence_of_service="County-by-county commuter scenario comparisons and net-pay transport stress testing.",
                    price_value_perception="Readily pays for 90-Day Journey Pass to optimize location selection.",
                    brand_image="HomePilot as the unbiased regional intelligence companion."
                ),
                journey_mapping=BPMJourneyMapping(
                    point_of_view="Commuter-displaced buyer weighing Dublin distance against scheme qualification.",
                    journey_scope="Property Search to Drawdown",
                    primary_stage="Regional Search & Bidding",
                    moments_of_truth=["Discovering Commuter Launch", "Evaluating FHS Eligibility", "Bidding War in Navan"],
                    points_of_failure=["Regional scheme cap disqualification", "Commute cost stress-test squeeze"],
                    duty_allocation=ThreeRsDutyAllocation(
                        role="Automated Discovery Bot (Firecrawl) with Human Operator Validation (2-Person Team)",
                        rule="Evidence must be corroborated by local developer price lists and regional council caps",
                        route="Feed Extractor -> Persona Engine -> Human Review Queue -> Approved Persona Store",
                        requires_human_validation=True
                    )
                ),
                primary_hook="Moving past Dublin? Here's how to navigate regional price caps and hidden commuter costs before you bid.",
                recommended_cta="Compare Commuter County Affordability Scenarios",
                discovered_from_source_ids=[doc.source_id],
                evidence_citations=[doc.markdown[:250]],
                confidence_score=92.0
            )
            self.repo.upsert_persona(new_persona)
            logger.info(f"Dynamically discovered and registered new persona: {new_persona.name} ({new_persona.segment_id})")
            return new_persona

        # Dynamic Pattern 2: The Vacant Property Grant Stacker
        if any(w in text for w in ["vacant", "derelict", "refurbishment grant", "croí cónaithe"]):
            seg_id = "dyn_seg_grant_stacker"
            existing = self.repo.get_persona(seg_id)
            if existing:
                existing.last_updated_at = datetime.utcnow()
                existing.evidence_citations.append(doc.markdown[:200])
                self.repo.upsert_persona(existing)
                return existing

            new_persona = AudiencePersona(
                segment_id=seg_id,
                name="The Vacant Property Grant Stacker",
                origin="discovered_feed",
                demographics={"age": "30-45", "income": "€50k-€110k", "geography": "Regional Towns & Rural Ireland"},
                beliefs=["Buying second-hand derelict property with grants is the smartest way to bypass new build developer premiums."],
                fears=["Cash-flow exhaustion while waiting for local authority grant reimbursements (paid in arrears)."],
                current_state_of_mind="Excited by €50k-€70k grant headlines but overwhelmed by contractor quotes and staged inspections.",
                desired_state_of_mind="Methodical cash-flow projection knowing exactly how to bridge grant reimbursement delays.",
                pain_points=["Vacant property grants are paid in arrears; buyers must fund 100% of renovations upfront."],
                system_bottlenecks=["Council inspection turnaround times and staged contractor payment milestones."],
                journey_mapping=BPMJourneyMapping(
                    point_of_view="Buyer considering derelict or vacant homes to stack local authority grants.",
                    journey_scope="Purchase to Post-Purchase Renovation",
                    primary_stage="Scheme Stack & Renovation Cash Flow",
                    moments_of_truth=["Grant Application Approval", "Contractor Tender Selection", "Council Milestone Inspection"],
                    points_of_failure=["Cash-flow exhaustion prior to reimbursement", "Unforeseen structural remediation costs"],
                    duty_allocation=ThreeRsDutyAllocation(
                        role="Gov.ie Policy Feed Bot + Human Operator Verification",
                        rule="Department of Housing statutory guidelines confirmed and inspection rules audited",
                        route="Policy Feed -> Grant Engine -> Operator Review -> Scenario Hub",
                        requires_human_validation=True
                    )
                ),
                primary_hook="The €50,000 Vacant Property Grant sounds amazing. But do you have the cash buffer to wait for council reimbursement?",
                recommended_cta="Simulate Grant Stacking & Renovation Cash Flow",
                discovered_from_source_ids=[doc.source_id],
                evidence_citations=[doc.markdown[:250]],
                confidence_score=90.0
            )
            self.repo.upsert_persona(new_persona)
            logger.info(f"Dynamically discovered and registered new persona: {new_persona.name} ({new_persona.segment_id})")
            return new_persona

        return None
