"""Section selector: AI-powered (default) or deterministic fallback."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_SECTION_DESCRIPTIONS = {
    "cover_page":             "Cover page with title, date, author, and client info. Always included.",
    "executive_summary":      "High-level narrative summary and bullet-point key findings for decision makers.",
    "market_overview":        "Market size, growth rate, geographic scope, and segment breakdown.",
    "key_metrics":            "Dashboard of KPIs and quantitative metrics in card layout.",
    "competitive_landscape":  "Profiles of key competitors including strengths, weaknesses, and market share.",
    "swot_analysis":          "Four-quadrant strengths, weaknesses, opportunities, threats grid.",
    "trend_analysis":         "Forward-looking trends shaping the market or industry.",
    "data_tables":            "Tabular data sets supporting the analysis.",
    "recommendations":        "Prioritised, actionable recommendations with owner and timeline.",
    "appendix":               "Supplementary notes and raw supporting data.",
}

_SYSTEM_PROMPT = """\
You are a report architect specializing in McKinsey-style consulting reports.

Given a list of available report sections (with descriptions) and the data fields \
present in the input, select and order the sections that will create the most \
coherent, professional market research report.

Rules:
1. Only include sections whose required data is present (do NOT invent missing data).
2. Always start with cover_page.
3. Place executive_summary early (after cover_page), if available.
4. Logical flow: market context → competition → analysis → forward-looking → actions → appendix.
5. Return ONLY a JSON array of section IDs, no explanation or markdown.

Example output: ["cover_page", "executive_summary", "market_overview", "competitive_landscape"]
"""


def select_sections_ai(
    data: dict,
    report_title: str | None = None,
    model: str = "claude-sonnet-4-5",
) -> list[str]:
    """Call the Anthropic API to select and order sections intelligently."""
    import anthropic

    from report_engine.sections import all_sections

    applicable_ids = [s.id for s in all_sections() if s.is_applicable(data)]
    present_fields = [k for k, v in data.items() if v is not None]

    section_info = "\n".join(
        f"  - {sid}: {_SECTION_DESCRIPTIONS.get(sid, '')}"
        for sid in applicable_ids
    )

    user_message = (
        f"Report title: {report_title or 'Market Research Report'}\n\n"
        f"Available sections (all have their required data present):\n{section_info}\n\n"
        f"Present data fields: {', '.join(present_fields)}\n\n"
        "Return the ordered JSON array of section IDs for this report."
    )

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=256,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    selected = json.loads(raw)

    # Validate: only allow IDs that are actually applicable
    valid = set(applicable_ids)
    return [s for s in selected if s in valid]


def select_sections_deterministic(data: dict) -> list[str]:
    """Return all applicable sections sorted by priority."""
    from report_engine.sections import all_sections

    applicable = [s for s in all_sections() if s.is_applicable(data)]
    applicable.sort(key=lambda s: s.priority)
    return [s.id for s in applicable]


def select_sections(
    data: dict,
    report_title: str | None = None,
    use_ai: bool = True,
    model: str = "claude-sonnet-4-5",
) -> list[str]:
    """
    Select and order report sections.

    Falls back to deterministic selection if use_ai=False or if the API call fails.
    """
    if not use_ai:
        return select_sections_deterministic(data)

    try:
        return select_sections_ai(data, report_title=report_title, model=model)
    except Exception as exc:
        logger.warning("AI section selection failed (%s); using deterministic fallback.", exc)
        return select_sections_deterministic(data)
