import logging
from typing import List, Optional, Dict, Any
from src.models.insight import (
    MarketInsight,
    TenQuestionsAnalysis,
    ScoringBreakdown,
    IcebergLayerAnalysis,
    SystemDynamicsContext
)
from src.models.campaign import CampaignOpportunity
from src.models.document import ExtractedDocument
from src.intelligence.grok_service import GrokService

logger = logging.getLogger(__name__)

class StrategicEngine:
    """Dynamic Systems Reasoning Engine for HomePilot.
    
    Applies Systems Thinking, the Iceberg Model, Stocks & Flows analysis,
    Bottleneck identification, and Second-Order feedback loop dynamics to
    interpret housing market developments.
    """

    STRATEGIC_DIMENSIONS = [
        "financial_confidence",
        "decision_intelligence",
        "reduced_uncertainty",
        "financial_outcomes",
        "homeownership_journey"
    ]

    # Systems Dynamics Archetypes mapped to the 12 Intelligence Categories
    CATEGORY_SYSTEM_PROFILES: Dict[str, Dict[str, str]] = {
        "FTBS": {
            "stock": "First-Time Buyer Purchasing Power & State Subsidy Pool",
            "flow": "Subsidy drawdown inflow vs. Price escalation outflow",
            "time_lag": "Immediate scheme application approval, but 3-6 month draw-down delay during construction",
            "bottleneck": "Eligibility cliff-edges and regional purchase price caps",
            "feedback_type": "reinforcing",
            "dominance": "Subsidies stimulate demand faster than housing supply responds, reinforcing price pressure",
            "second_order": "Grant increases can induce developers to raise base prices to match subsidy ceiling, shifting cost burdens"
        },
        "MFPL": {
            "stock": "Lender Mortgage Quotas & Household Debt Capacity",
            "flow": "Monthly debt service outflow vs. Net disposable income inflow",
            "time_lag": "Central Bank rate decisions take 30-90 days to pass through to fixed/variable mortgage offers",
            "bottleneck": "Central Bank 4.0x LTI ceiling and bank stress-testing buffers (+1.5% to +2.0% above offer)",
            "feedback_type": "balancing",
            "dominance": "Macroprudential rules act as a cooling balancing loop, restricting runaway borrowing growth",
            "second_order": "Tighter stress testing pushes marginal buyers into high-rent tenancy, delaying deposit accumulation"
        },
        "HSRD": {
            "stock": "Active Residential Housing Inventory (Commencements to Completions)",
            "flow": "Construction commencement inflow vs. Sales transaction outflow",
            "time_lag": "18 to 24 month structural delay between site acquisition/planning and key handover",
            "bottleneck": "Infrastructure connections (water/substations) and skilled labor availability",
            "feedback_type": "balancing",
            "dominance": "Supply response is sluggish compared to rapid shifts in consumer demand",
            "second_order": "New phase releases in commuter towns shift local infrastructure demand (schools/transit) before civic upgrades occur"
        },
        "IRPM": {
            "stock": "Aggregate Market Listings & Buyer Price Expectations",
            "flow": "New property listings inflow vs. Delisting/Contract agreement outflow",
            "time_lag": "Asking price indices reflect current sentiment; actual PPR sold prices carry a 60-90 day conveyancing lag",
            "bottleneck": "Scarcity of turnkey second-hand homes in commuter corridors",
            "feedback_type": "reinforcing",
            "dominance": "Bidding wars and scarcity narratives reinforce aggressive buyer bidding above asking price",
            "second_order": "Bidding above valuation creates mortgage shortfall where buyers must fund valuation gap in cash"
        },
        "AFFR": {
            "stock": "Household Liquid Savings & Emergency Cash Buffer",
            "flow": "Monthly savings inflow vs. High rent and non-mortgage acquisition cost outflow",
            "time_lag": "3 to 5 years required for average household to build 10% deposit + fees buffer",
            "bottleneck": "Closing costs (legal, stamp duty, survey, valuation) totaling 3-5% on top of deposit",
            "feedback_type": "balancing",
            "dominance": "Rent inflation drains monthly cash flow, slowing deposit accumulation",
            "second_order": "Depleting entire liquid savings for deposit leaves zero emergency buffer, creating immediate post-purchase financial distress"
        }
    }

    @classmethod
    def evaluate_ten_questions(
        cls,
        doc: ExtractedDocument,
        category: str,
        score_breakdown: ScoringBreakdown,
        grok_service: Optional[GrokService] = None
    ) -> TenQuestionsAnalysis:
        """Dynamically evaluates the 10 Strategic Questions through Systems Thinking and the Iceberg Model."""
        title = doc.title or "Irish Housing Market Development"
        sys_profile = cls.CATEGORY_SYSTEM_PROFILES.get(category, {
            "stock": "Market Information & Buyer Confidence",
            "flow": "Information dissemination inflow vs. Misconception outflow",
            "time_lag": "Varies by regulatory and market cycle",
            "bottleneck": "Fragmented data sources and complex legal terminology",
            "feedback_type": "balancing",
            "dominance": "Balanced information improves buyer decision speed",
            "second_order": "Clarity reduces search duration and legal abortive costs"
        })

        # 1. Iceberg Model Decomposition
        iceberg = IcebergLayerAnalysis(
            event=f"Published development: '{title}'",
            pattern_of_behaviour=f"Persistent recurring dynamics in {category} affecting transaction velocity and buyer readiness.",
            supporting_structure=f"Irish regulatory framework, Central Bank macroprudential rules, and lender underwriting policies.",
            mental_model="Buyer misconception that mortgage approval equals complete financial readiness, ignoring second-order costs."
        )

        # 2. System Dynamics Context (Stocks, Flows, Bottlenecks, Loops)
        sys_dynamics = SystemDynamicsContext(
            stock_impacted=sys_profile["stock"],
            flow_direction=sys_profile["flow"],
            time_lag=sys_profile["time_lag"],
            bottleneck_identified=sys_profile["bottleneck"],
            feedback_loop_type=sys_profile["feedback_type"],
            dominance_shifting=sys_profile["dominance"],
            second_order_effect=sys_profile["second_order"]
        )

        # 3. Dynamic Answering of the 10 Strategic Questions
        q1 = f"Verified market development: '{title}' documented in {category}."
        q2 = f"Why it matters: Directly impacts the system stock of '{sys_dynamics.stock_impacted}', with a time lag of {sys_dynamics.time_lag}."
        q3 = "Who is affected: Prospective buyers at the critical bottleneck stage where mortgage readiness meets physical closing realities."
        q4 = f"Customer problem: The bottleneck constraint '{sys_dynamics.bottleneck_identified}', compounded by second-order effects: {sys_dynamics.second_order_effect}."
        q5 = "HomePilot connection: Transitions users from first-order linear thinking (borrowing limits) to holistic homeownership systems thinking."
        q6 = "Product capability: HomePilot Scenario Simulator, Stress-Testing Engine, and Total Acquisition Cost Buffer Calculator."
        q7 = "Supports existing campaign: Strengthens the 'Mortgage-Ready vs. Homeownership-Ready' and 'The Real Cost of Buying' campaign narratives."
        q8 = f"Creates new campaign: Educational asset breaking down the second-order consequences: '{sys_dynamics.second_order_effect}'."
        q9 = f"Time sensitivity: High. Governed by time delay ({sys_dynamics.time_lag}) before market behaviour becomes entrenched."
        q10 = "Additional evidence needed: Independent verification from Central Bank lending statistics, PPR transaction registers, and CSO dwelling figures."

        return TenQuestionsAnalysis(
            q1_what_happened=q1,
            q2_why_it_matters=q2,
            q3_who_is_affected=q3,
            q4_customer_problem=q4,
            q5_homepilot_connection=q5,
            q6_product_capability=q6,
            q7_supports_existing_campaign=q7,
            q8_creates_new_campaign=q8,
            q9_time_sensitivity=q9,
            q10_additional_evidence_needed=q10,
            iceberg=iceberg,
            system_dynamics=sys_dynamics
        )

    @classmethod
    def cluster_into_campaign(cls, insights: List[MarketInsight], theme_title: str, dimension: str) -> CampaignOpportunity:
        """Clusters related insights into a systems-thinking campaign package."""
        campaign_id = f"cmp_{dimension}_{len(insights)}"
        
        # Aggregate second-order insights from cluster
        second_order_points = []
        for ins in insights:
            if ins.ten_questions and ins.ten_questions.system_dynamics:
                second_order_points.append(ins.ten_questions.system_dynamics.second_order_effect)

        hook = "Getting bank approval is one milestone. Understanding the system dynamics of homeownership is another."
        problem = "Prospective buyers fall victim to first-order linear thinking—assuming finding a property and borrowing approval is the end of the journey, unaware of systemic bottlenecks, cash flow delays, and hidden closing costs."

        return CampaignOpportunity(
            campaign_id=campaign_id,
            theme_title=theme_title,
            strategic_dimension=dimension,
            central_customer_problem=problem,
            homepilot_positioning_hook=hook,
            product_feature_cta="Use HomePilot's Scenario Engine to simulate second-order cash flows, stress rates, and reserve buffers.",
            insight_ids=[ins.insight_id for ins in insights],
            status="ready_for_review"
        )
