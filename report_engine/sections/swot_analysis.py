from report_engine.sections import BaseSection, register


@register
class SWOTAnalysis(BaseSection):
    id = "swot_analysis"
    display_name = "SWOT Analysis"
    required_fields = ["swot"]
    optional_fields = []
    priority = 40
