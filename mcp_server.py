"""
Dossier MCP Server

Exposes a single tool to any MCP client:

  generate_report  — render a dossier-compatible dict to a PDF

No API key required. No AI calls inside the tool. The calling agent
(Claude Code, GPT-4, any LLM harness) is responsible for research and
data formatting — this tool is a pure PDF renderer.

Typical usage from any agent:
    result = generate_report({
        "title": "Global Fintech Market 2025",
        "summary": "...",
        "key_findings": ["...", "..."],
        "market_size": "$312B",
        ...
    })
    # → {"success": True, "output_path": "~/reports/global_fintech_market_2025.pdf", ...}
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP

mcp = FastMCP(
    name="dossier",
    instructions=(
        "Dossier renders consulting-grade PDF reports from structured data. "
        "It makes no AI calls — you supply the research and formatting.\n\n"
        "Workflow:\n"
        "1. Research the topic using your own tools and knowledge.\n"
        "2. Format findings as a data dict (see generate_report schema).\n"
        "3. Call generate_report(data) — a PDF is written to ~/reports/.\n\n"
        "Required field: title. All others are optional — sections are "
        "auto-selected based on which fields are present."
    ),
)


@mcp.tool()
def generate_report(
    data: dict,
    output_path: str | None = None,
    title: str | None = None,
) -> dict:
    """
    Render structured research data into a consulting-grade PDF report.
    No API key or AI calls required — purely deterministic rendering.

    Args:
        data:        Research data dict. Must contain at least {"title": "..."}.
                     Supported fields:
                       title, date, subtitle, author, client, confidentiality,
                       summary, key_findings,
                       market_size, market_growth, market_description, market_segments,
                       metrics     — list of {label, value, change?, trend?, description?}
                       competitors — list of {name, description, strengths?, weaknesses?, ...}
                       swot        — {strengths, weaknesses, opportunities, threats}
                       trends      — list of {title, description, impact, timeframe?, drivers?}
                       tables      — list of {title, headers, rows, notes?}
                       recommendations — list of {title, description, priority?, timeline?, owner?}
                       appendix, raw_data
        output_path: Where to write the PDF. Defaults to ~/reports/<title-slug>.pdf
        title:       Override the report title.

    Returns:
        {"success": bool, "output_path": str, "sections_used": list[str], "error": str | None}
    """
    from report_engine.mcp_tool import generate_report as _generate

    if output_path is None:
        reports_dir = Path.home() / "reports"
        reports_dir.mkdir(exist_ok=True)
        slug = (title or data.get("title") or "report")[:60]
        slug = "".join(c if c.isalnum() or c in "-_ " else "" for c in slug)
        slug = slug.strip().replace(" ", "_").lower()
        output_path = str(reports_dir / f"{slug}.pdf")

    return _generate(data, output_path=output_path, title=title)


if __name__ == "__main__":
    mcp.run()
