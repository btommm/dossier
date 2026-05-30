from report_engine.sections import BaseSection, register


@register
class TrendAnalysis(BaseSection):
    id = "trend_analysis"
    display_name = "Trend Analysis"
    required_fields = ["trends"]
    optional_fields = ["trends_summary"]
    priority = 35
