from report_engine.sections import BaseSection, register


@register
class MarketOverview(BaseSection):
    id = "market_overview"
    display_name = "Market Overview"
    required_fields = ["market_size", "market_growth", "market_description"]
    optional_fields = ["market_segments", "geographic_scope"]
    priority = 20
