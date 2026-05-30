from report_engine.sections import BaseSection, register


@register
class KeyMetrics(BaseSection):
    id = "key_metrics"
    display_name = "Key Metrics"
    required_fields = ["metrics"]
    optional_fields = []
    priority = 25
