from report_engine.sections import BaseSection, register


@register
class DataTables(BaseSection):
    id = "data_tables"
    display_name = "Data Tables"
    required_fields = ["tables"]
    optional_fields = []
    priority = 50
