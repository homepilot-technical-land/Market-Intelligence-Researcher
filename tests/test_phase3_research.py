import pytest
from src.connectors.api_connectors import PropertyPriceRegisterConnector, CSOStatConnector, RTBRentIndexConnector
from src.intelligence.daily_briefing import DailyBriefingGenerator
from src.storage.repository import IntelligenceRepository

def test_ppr_connector_county_affordability():
    benchmarks = PropertyPriceRegisterConnector.calculate_county_affordability_benchmarks(county="Meath")
    assert benchmarks["county"] == "Meath"
    assert benchmarks["sample_size"] >= 10
    assert benchmarks["median_starter_home_price"] > 300000.0
    assert benchmarks["first_home_scheme_cap"] == 375000.0
    assert "cap_breach_rate_percent" in benchmarks
    assert benchmarks["cap_breach_rate_percent"] >= 0.0

def test_cso_stat_connector():
    indicators = CSOStatConnector.fetch_housing_market_indicators()
    assert "table_hpm05" in indicators
    assert "table_nda02" in indicators
    hpm05 = indicators["table_hpm05"]
    assert hpm05["national_annual_inflation_rate_percent"] > 0
    assert hpm05["first_time_buyer_median_national_price_eur"] > 0

def test_rtb_rent_connector():
    delta = RTBRentIndexConnector.calculate_buy_vs_rent_differential(county="Meath", purchase_price=375000.0)
    assert delta["county"] == "Meath"
    assert delta["monthly_market_rent"] > 1000.0
    assert delta["monthly_mortgage_repayment"] > 1000.0
    assert "annual_cash_flow_advantage_eur" in delta

def test_daily_briefing_generator():
    repo = IntelligenceRepository()
    generator = DailyBriefingGenerator(repository=repo)
    briefing = generator.generate_morning_briefing(county_focus="Meath")

    assert briefing.briefing_id.startswith("briefing_")
    assert "County Meath" in briefing.markdown_report
    assert "National Housing Inflation" in briefing.markdown_report
    assert "Closing Cost Liquidity Trap" in briefing.systemic_bottlenecks
    assert "dyn_seg_commuter_cap_straddler" in briefing.affected_personas
    assert len(briefing.affected_personas) >= 3
    assert "daily_briefings" in repo._store
