from report_engine.sections import BaseSection, register


@register
class Recommendations(BaseSection):
    id = "recommendations"
    display_name = "Recommendations"
    required_fields = ["recommendations"]
    optional_fields = ["recommendations_summary"]
    priority = 70
