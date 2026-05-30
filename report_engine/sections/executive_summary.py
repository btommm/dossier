from report_engine.sections import BaseSection, register


@register
class ExecutiveSummary(BaseSection):
    id = "executive_summary"
    display_name = "Executive Summary"
    required_fields = ["summary", "key_findings"]
    optional_fields = []
    priority = 10
