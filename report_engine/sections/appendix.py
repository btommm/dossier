from report_engine.sections import BaseSection, register


@register
class Appendix(BaseSection):
    id = "appendix"
    display_name = "Appendix"
    required_fields = ["appendix", "raw_data"]
    optional_fields = []
    priority = 90
