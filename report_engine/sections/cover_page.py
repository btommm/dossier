from report_engine.sections import BaseSection, register


@register
class CoverPage(BaseSection):
    id = "cover_page"
    display_name = "Cover Page"
    required_fields = ["title"]
    optional_fields = ["date", "subtitle", "author", "client", "confidentiality"]
    priority = 0
