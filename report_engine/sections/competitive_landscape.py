from report_engine.sections import BaseSection, register


@register
class CompetitiveLandscape(BaseSection):
    id = "competitive_landscape"
    display_name = "Competitive Landscape"
    required_fields = ["competitors"]
    optional_fields = ["competitive_summary"]
    priority = 30
