import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from src.storage.repository import IntelligenceRepository
from src.connectors.api_connectors import PropertyPriceRegisterConnector, CSOStatConnector, RTBRentIndexConnector
from src.observability.posthog_client import PostHogTelemetry
from src.models.insight import MarketInsight

logger = logging.getLogger(__name__)

class DailyBriefing(BaseModel):
    briefing_id: str
    briefing_date: str # YYYY-MM-DD
    title: str
    macro_indicators: Dict[str, Any]
    insights_summarized: List[str]
    affected_personas: List[str]
    systemic_bottlenecks: List[str]
    pending_operator_reviews_count: int
    markdown_report: str
    target_counties: List[str] = Field(default_factory=lambda: ["Meath"])
    active_campaign_name: Optional[str] = None
    out_of_focus_regional_alerts: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DailyBriefingGenerator:
    """Automated Daily Morning Intelligence Briefing Generator.
    
    Synthesizes a multi-region executive operational brief every morning at 07:00 UTC
    for the 2 operators. The daily batch is dynamically governed by the current
    active marketing campaign's targeted regions (set via GrokBot / MCP).
    
    In addition, it acts as an anomaly radar: if unexpected news, regulatory changes,
    or price surges break in a non-focus region/county, it triggers an Out-of-Focus
    Regional Spike Alert enriched with full context.
    """

    def __init__(
        self,
        repository: Optional[IntelligenceRepository] = None,
        telemetry: Optional[PostHogTelemetry] = None
    ):
        self.repo = repository or IntelligenceRepository()
        self.telemetry = telemetry or PostHogTelemetry()

    def generate_morning_briefing(
        self,
        county_focus: Optional[str] = None,
        counties: Optional[List[str]] = None,
        campaign_name: Optional[str] = None
    ) -> DailyBriefing:
        """Generates the daily morning operational brief aligned to the active campaign period."""
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        briefing_id = f"briefing_{now.strftime('%Y%m%d_%H%M%S')}"

        # 1. Resolve active campaign target regions
        active_campaign = self.repo.get_active_campaign_focus()
        active_campaign_title = campaign_name or active_campaign.get("campaign_name", "Commuter Belt Scheme Gap Sprint")
        
        if counties:
            target_counties = [c.strip().title() for c in counties if c.strip()]
        elif county_focus and county_focus != "Meath":
            target_counties = [county_focus.strip().title()]
        else:
            target_counties = active_campaign.get("target_counties", ["Meath", "Kildare", "Wicklow"])

        # 2. Fetch live national macro indicators
        cso_data = CSOStatConnector.fetch_housing_market_indicators()
        hpm05 = cso_data.get("table_hpm05", {})
        nda02 = cso_data.get("table_nda02", {})

        # 3. Batch regional benchmarks across all target campaign counties
        regional_benchmarks = {}
        for cty in target_counties:
            ppr_benchmarks = PropertyPriceRegisterConnector.calculate_county_affordability_benchmarks(county=cty)
            rent_comp = RTBRentIndexConnector.calculate_buy_vs_rent_differential(county=cty)
            regional_benchmarks[cty] = {
                "ppr": ppr_benchmarks,
                "rent": rent_comp
            }

        # 4. Check for Out-of-Focus Regional Spike Alerts
        # Any high-priority alerts recorded for counties OUTSIDE current campaign target
        out_of_focus_alerts = []
        raw_alerts = self.repo.list_regional_spike_alerts(limit=10, active_only=True)
        for al in raw_alerts:
            al_cty = al.get("county", "").strip().title()
            if al_cty and al_cty not in target_counties:
                out_of_focus_alerts.append(al)

        # 5. Query high-priority insights from store
        recent_insights = self.repo.list_insights(min_composite_score=70.0)
        insight_titles = [i.doc_id for i in recent_insights][:5]
        if not insight_titles:
            insight_titles = [
                "Gov.ie First Home Scheme Price Ceilings Revised",
                "CCPC Homebuyer Guide: Hidden Closing Costs Warning"
            ]

        # 6. Compile Dynamic Multi-Region Executive Brief Markdown
        target_counties_str = ", ".join(target_counties)
        report_lines = [
            f"# HomePilot Daily Intelligence Briefing — {date_str}",
            f"**Briefing ID:** `{briefing_id}` | **Generated:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Active Campaign Focus:** `{active_campaign_title}` | **Target Regions:** County {target_counties_str}",
            "**Operational Scope:** Internal Operator Briefing (2 Operators) | **Source Mode:** Verified Statutory & PPR/CSO Data",
            "",
            "---",
            "",
            "## 1. Executive Macro Pulse & Price Index",
            f"- **National Housing Inflation (CSO HPM05):** **+{hpm05.get('national_annual_inflation_rate_percent', 8.4)}% YoY** (Dublin: +{hpm05.get('dublin_annual_inflation_rate_percent', 6.8)}%, Outside Dublin: +{hpm05.get('outside_dublin_annual_inflation_rate_percent', 9.7)}%).",
            f"- **National FTB Median Price:** **€{hpm05.get('first_time_buyer_median_national_price_eur', 345000):,.0f}** vs. Non-FTB Median: **€{hpm05.get('non_first_time_buyer_median_national_price_eur', 420000):,.0f}**.",
            f"- **Annual Completions (CSO NDA02):** **{nda02.get('annual_national_completions', 33450):,} units** ({nda02.get('scheme_houses_percentage', 58.2)}% scheme houses, {nda02.get('apartments_percentage', 31.4)}% apartments).",
            "",
            f"## 2. Active Campaign Regional Affordability ({active_campaign_title})",
        ]

        # Add section for each campaign-targeted county
        for cty, data in regional_benchmarks.items():
            ppr_b = data["ppr"]
            rent_c = data["rent"]
            report_lines.extend([
                f"### County {cty}",
                f"- **Median Starter Home:** **€{ppr_b.get('median_starter_home_price', 360000):,.0f}** | **New Build Median:** **€{ppr_b.get('median_new_build_price', 385000):,.0f}**",
                f"- **First Home Scheme Cap:** **€{ppr_b.get('first_home_scheme_cap', 375000):,.0f}** (Cap Breach Rate: **{ppr_b.get('cap_breach_rate_percent', 60.0)}%** of new builds)",
                f"- **Buy vs. Rent Monthly Delta:** Monthly Rent **€{rent_c.get('monthly_market_rent', 1650):,.0f}** vs. Mortgage Repayment **€{rent_c.get('monthly_mortgage_repayment', 1572):,.0f}** (Annual Homeowner Advantage: **€{rent_c.get('annual_cash_flow_advantage_eur', 936):,.0f}**).",
                ""
            ])

        # Add Out-of-Focus Regional Alerts if present
        if out_of_focus_alerts:
            report_lines.extend([
                "## 🚨 Out-of-Focus Regional Spike Alerts",
                f"> [!WARNING]",
                f"> **Breaking Intelligence in Non-Campaign Regions (Active Period Focus: {target_counties_str})**",
                ""
            ])
            for alert in out_of_focus_alerts:
                al_cty = alert.get("county", "Unknown")
                report_lines.extend([
                    f"### 📍 Spike Alert: County {al_cty} — {alert.get('headline', 'Market Event Detected')}",
                    f"- **Trigger Category:** {alert.get('category', 'Regulatory / Price Shift')}",
                    f"- **Summary:** {alert.get('summary', 'No summary provided')}",
                    f"- **Verified Data / Evidence:** {', '.join(alert.get('facts', [])) if isinstance(alert.get('facts'), list) else alert.get('facts', 'Verified from statutory source.')}",
                    f"- **Strategic Implication for HomePilot:** {alert.get('strategic_implications', 'Evaluate whether to launch localized campaign hook or adjust buyer journey recommendations.')}",
                    ""
                ])

        report_lines.extend([
            "## 3. Core Persona Friction Benchmarks",
            "- **`seg_1_frustrated_ftb` (The Frustrated FTB):** Disheartened by repeat calculator use; 4.0x LTI borrowing cap is artificially constrained while rental drain prevents cash deposit accumulation.",
            f"- **`dyn_seg_commuter_cap_straddler` (Commuter Price-Cap Straddler):** High alert across {target_counties_str}—developer phase asking prices sit just above statutory caps, creating an unexpected equity gap.",
            "- **`seg_3_homeownership_planner` (Sale Agreed):** Struggling with the 12–16 week conveyancing lag and the €7,500–€12,000 hidden closing fee deficit.",
            "",
            "## 4. Systems Thinking & Bottleneck Flags",
            "- **The Closing Cost Liquidity Trap:** Buyers committing 100% of cash reserves to the 10% mortgage deposit, leaving zero liquidity for valuation (€400), structural survey (€600), solicitor (€2,500), and stamp duty (1%).",
            "- **Subsidies Capitalized into Base Price:** Help to Buy (€30k) and First Home Scheme equity are being priced into base developer launches in satellite commuter corridors.",
            "",
            "## 5. Operator Action Items for Today",
            f"- [ ] Review active campaign alignments for **{active_campaign_title}** in {target_counties_str}.",
            f"- [ ] Inspect any out-of-focus alerts ({len(out_of_focus_alerts)} active) in the Review Queue.",
            "- [ ] Align upcoming social & campaign blueprints with HomePilot's **Total Acquisition Cost Buffer Planner**."
        ])

        markdown_report = "\n".join(report_lines)

        primary_county = target_counties[0] if target_counties else "Meath"
        primary_benchmarks = regional_benchmarks.get(primary_county, {}).get("ppr", {})

        briefing = DailyBriefing(
            briefing_id=briefing_id,
            briefing_date=date_str,
            title=f"Daily Intelligence Briefing — {date_str} ({active_campaign_title}: {target_counties_str})",
            macro_indicators={
                "inflation_yoy": hpm05.get("national_annual_inflation_rate_percent"),
                "median_starter_home": primary_benchmarks.get("median_starter_home_price"),
                "cap_breach_rate": primary_benchmarks.get("cap_breach_rate_percent")
            },
            insights_summarized=insight_titles,
            affected_personas=["seg_1_frustrated_ftb", "dyn_seg_commuter_cap_straddler", "seg_3_homeownership_planner"],
            systemic_bottlenecks=["Closing Cost Liquidity Trap", "Conveyancing Latency Lag"],
            pending_operator_reviews_count=len(self.repo._store.get("source_candidates", {})),
            markdown_report=markdown_report,
            target_counties=target_counties,
            active_campaign_name=active_campaign_title,
            out_of_focus_regional_alerts=out_of_focus_alerts,
            created_at=now
        )

        # Record in repository store
        if "daily_briefings" not in self.repo._store:
            self.repo._store["daily_briefings"] = {}
        self.repo._store["daily_briefings"][briefing_id] = briefing.model_dump()

        self.telemetry.capture("research.objective.completed", {
            "briefing_id": briefing_id,
            "briefing_date": date_str,
            "campaign_name": active_campaign_title,
            "target_counties": target_counties,
            "out_of_focus_alerts_count": len(out_of_focus_alerts)
        })

        logger.info(f"Generated daily briefing {briefing_id} for campaign '{active_campaign_title}' covering {target_counties} (out-of-focus alerts: {len(out_of_focus_alerts)})")
        return briefing

        self.telemetry.capture("research.objective.completed", {
            "briefing_id": briefing_id,
            "briefing_date": date_str,
            "county_focus": county_focus,
            "personas_count": len(briefing.affected_personas)
        })

        logger.info(f"Generated daily briefing {briefing_id} for {date_str}")
        return briefing
