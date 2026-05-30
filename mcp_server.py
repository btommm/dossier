"""
Dossier MCP Server

Exposes two tools to any MCP client (Claude Code, Claude Desktop, etc.):

  research_topic   — web-search a topic, return structured data
  generate_report  — render a dossier-compatible dict to a PDF

Typical usage from an agent:
    data   = research_topic("Global fintech market 2025")
    result = generate_report(data, "/tmp/fintech.pdf")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the package is importable when launched as a script
sys.path.insert(0, str(Path(__file__).parent))

# Load .env so ANTHROPIC_API_KEY is available
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from fastmcp import FastMCP

mcp = FastMCP(
    name="dossier",
    instructions=(
        "Dossier generates professional consulting-style PDF reports from structured research data. "
        "Use research_topic to gather live data on any topic, then generate_report to render the PDF. "
        "Both tools can be used independently or chained together."
    ),
)


@mcp.tool()
def research_topic(
    topic: str,
    depth: str = "standard",
    date: str | None = None,
) -> dict:
    """
    Research a topic using Claude + web search and return dossier-compatible data.

    Args:
        topic: The research subject (e.g. "Global SaaS market 2025",
               "Climate tech VC landscape", "Nvidia competitive analysis")
        depth: How thorough to be — "quick" (~6 searches), "standard" (~12),
               "deep" (~20+ searches)
        date:  Report date label (e.g. "May 2025"). Defaults to current month/year.

    Returns:
        A dict with fields like summary, key_findings, market_size, metrics,
        competitors, swot, trends, recommendations, etc. Pass directly to
        generate_report() to produce a PDF.
    """
    from report_engine.research import research_topic as _research

    if depth not in ("quick", "standard", "deep"):
        depth = "standard"

    return _research(topic, depth=depth, date=date)  # type: ignore[arg-type]


@mcp.tool()
def generate_report(
    data: dict,
    output_path: str | None = None,
    title: str | None = None,
    use_ai: bool = True,
) -> dict:
    """
    Render a dossier-compatible data dict into a consulting-grade PDF report.

    Args:
        data:        Research data dict — typically the output of research_topic().
                     Must contain at least {"title": "..."}.
        output_path: Where to write the PDF. Defaults to ~/reports/<slug>.pdf
        title:       Override the report title.
        use_ai:      Use Claude to select and order sections intelligently.
                     Set False for faster, deterministic section ordering.

    Returns:
        {"success": bool, "output_path": str, "sections_used": list, "error": str | None}
    """
    from report_engine.mcp_tool import generate_report as _generate

    # Default output path: ~/reports/<slug>.pdf
    if output_path is None:
        reports_dir = Path.home() / "reports"
        reports_dir.mkdir(exist_ok=True)
        slug = (data.get("title") or "report")[:60]
        slug = "".join(c if c.isalnum() or c in "-_ " else "" for c in slug)
        slug = slug.strip().replace(" ", "_").lower()
        output_path = str(reports_dir / f"{slug}.pdf")

    return _generate(data, output_path=output_path, title=title, use_ai=use_ai)


if __name__ == "__main__":
    mcp.run()
