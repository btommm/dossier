"""
MCP-ready stub for the report engine.

Drop this into an MCP server to expose report generation as a tool call.
The function signature is intentionally clean: plain dict in, plain dict out.
"""

from __future__ import annotations

from pathlib import Path


def generate_report(
    data: dict,
    output_path: str,
    title: str | None = None,
    use_ai: bool = True,
) -> dict:
    """
    Generate a professional PDF report from structured research data.

    Intelligently selects and orders sections based on available data fields.
    Supported data keys: title, date, subtitle, author, client, summary, key_findings,
    market_size, market_growth, market_description, competitors, swot, tables,
    metrics, trends, recommendations, appendix, raw_data.

    Args:
        data:        Input data dict. Must include 'title'. All other fields optional.
        output_path: Filesystem path for the generated PDF (e.g. "/tmp/report.pdf").
        title:       Optional title override (applied on top of data['title']).
        use_ai:      If True, use the Anthropic API to select/order sections.
                     Falls back to deterministic ordering on API failure.

    Returns:
        {
            "success": bool,
            "output_path": str,
            "sections_used": list[str],
            "error": str | None,
        }
    """
    from report_engine.renderer import generate
    from report_engine.schema import ReportInput
    from report_engine.selector import select_sections

    if title:
        data = {**data, "title": title}

    try:
        report = ReportInput.model_validate(data)
    except Exception as exc:
        return {"success": False, "output_path": output_path, "sections_used": [], "error": str(exc)}

    data_dict = report.model_dump()
    section_ids = select_sections(data_dict, report_title=data_dict.get("title"), use_ai=use_ai)

    try:
        generate(data_dict, section_ids, Path(output_path))
        return {"success": True, "output_path": output_path, "sections_used": section_ids, "error": None}
    except Exception as exc:
        return {"success": False, "output_path": output_path, "sections_used": section_ids, "error": str(exc)}
