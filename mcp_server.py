"""
Dossier MCP Server

Exposes one primary tool to any MCP client (Claude Code, Claude Desktop, etc.):

  generate_report  — render a dossier-compatible dict to a PDF

The recommended workflow is for Claude to perform research using its own
web search capabilities, format the results into the dossier schema, then
call generate_report() to produce the PDF. No API key required.

If you have ANTHROPIC_API_KEY set in .env or the environment, the optional
research_topic tool is also available for standalone research workflows.

Typical agent usage (no API key needed):
    # Claude researches the topic, then calls:
    result = generate_report(data, title="My Report")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastmcp import FastMCP

mcp = FastMCP(
    name="dossier",
    instructions=(
        "Dossier renders consulting-grade PDF reports from structured data. "
        "RECOMMENDED WORKFLOW — no API key needed:\n"
        "1. Research the topic yourself using web search and your own knowledge.\n"
        "2. Format the findings as a dossier data dict (see generate_report schema).\n"
        "3. Call generate_report(data) to produce the PDF.\n\n"
        "The data dict must have 'title'. All other fields are optional — only sections "
        "with data present will be included. Key fields: summary, key_findings, "
        "market_size, market_growth, metrics, competitors, swot, trends, "
        "recommendations, tables, appendix."
    ),
)


@mcp.tool()
def generate_report(
    data: dict,
    output_path: str | None = None,
    title: str | None = None,
) -> dict:
    """
    Render a dossier-compatible data dict into a consulting-grade PDF report.
    No API key required.

    Args:
        data:        Research data dict. Must contain at least {"title": "..."}.
                     Supported fields:
                       title, date, subtitle, author, client, confidentiality,
                       summary, key_findings,
                       market_size, market_growth, market_description, market_segments,
                       metrics (list of {label, value, change, trend, description}),
                       competitors (list of {name, description, strengths, weaknesses, ...}),
                       swot ({strengths, weaknesses, opportunities, threats}),
                       trends (list of {title, description, impact, timeframe, drivers}),
                       tables (list of {title, headers, rows, notes}),
                       recommendations (list of {title, description, priority, timeline, owner}),
                       appendix, raw_data
        output_path: Where to write the PDF. Defaults to ~/reports/<slug>.pdf
        title:       Override the report title.

    Returns:
        {"success": bool, "output_path": str, "sections_used": list, "error": str | None}
    """
    from report_engine.mcp_tool import generate_report as _generate

    if output_path is None:
        reports_dir = Path.home() / "reports"
        reports_dir.mkdir(exist_ok=True)
        slug = (data.get("title") or title or "report")[:60]
        slug = "".join(c if c.isalnum() or c in "-_ " else "" for c in slug)
        slug = slug.strip().replace(" ", "_").lower()
        output_path = str(reports_dir / f"{slug}.pdf")

    return _generate(data, output_path=output_path, title=title, use_ai=False)


@mcp.tool()
def research_topic(
    topic: str,
    depth: str = "standard",
    date: str | None = None,
) -> dict:
    """
    Research a topic using Claude + web search and return dossier-compatible data.
    Requires ANTHROPIC_API_KEY to be set in the environment or .env file.

    Prefer letting Claude Code research natively and calling generate_report directly —
    that workflow needs no API key. Use this tool only for standalone/scripted pipelines.

    Args:
        topic: The research subject
        depth: "quick" (~6 searches), "standard" (~12), "deep" (~20+)
        date:  Report date label (e.g. "June 2026"). Defaults to current month/year.

    Returns:
        A dossier-compatible dict. Pass directly to generate_report() to produce a PDF.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {
            "error": (
                "ANTHROPIC_API_KEY is not set. For keyless usage, have Claude research "
                "the topic and call generate_report() directly with the formatted data."
            )
        }

    from report_engine.research import research_topic as _research

    if depth not in ("quick", "standard", "deep"):
        depth = "standard"

    return _research(topic, depth=depth, date=date)  # type: ignore[arg-type]


if __name__ == "__main__":
    mcp.run()
