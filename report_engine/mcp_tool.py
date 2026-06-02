"""
MCP-ready stub for dossier — generate_report only, no API calls.

Typical agent usage:
    result = generate_report(data, "/tmp/report.pdf")
"""

from __future__ import annotations

from pathlib import Path


def generate_report(
    data: dict,
    output_path: str,
    title: str | None = None,
) -> dict:
    """
    Generate a professional PDF report from structured research data.

    Args:
        data:        Input data dict. Must include 'title'. All other fields optional.
        output_path: Filesystem path for the generated PDF.
        title:       Optional title override.

    Returns:
        {"success": bool, "output_path": str, "sections_used": list[str], "error": str | None}
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
    section_ids = select_sections(data_dict)

    try:
        generate(data_dict, section_ids, Path(output_path))
        return {"success": True, "output_path": output_path, "sections_used": section_ids, "error": None}
    except Exception as exc:
        return {"success": False, "output_path": output_path, "sections_used": section_ids, "error": str(exc)}
