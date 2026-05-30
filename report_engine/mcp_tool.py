"""
MCP-ready stubs for dossier.

Drop these into an MCP server to expose research + report generation as tool calls.
All functions take plain Python types and return plain dicts — no CLI, no side effects
beyond writing the PDF file.

Typical agent usage:
    data   = research_topic("Global SaaS market 2025")
    result = generate_report(data, "/tmp/saas_report.pdf")
"""

from __future__ import annotations

from pathlib import Path


def research_topic(
    topic: str,
    depth: str = "standard",
    date: str | None = None,
) -> dict:
    """
    Research a topic using Claude + web search and return a dossier-compatible data dict.

    Args:
        topic:  Research topic (e.g. "Global SaaS Market 2025")
        depth:  "quick" (~6 searches), "standard" (~12), "deep" (~20+)
        date:   Report date label — defaults to current month/year

    Returns:
        Dict matching the dossier ReportInput schema.
        Pass directly to generate_report() to produce a PDF.
    """
    from report_engine.research import research_topic as _research
    return _research(topic, depth=depth, date=date)  # type: ignore[arg-type]


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
