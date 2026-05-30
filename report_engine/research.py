"""
Research engine: uses Claude + web search to generate dossier-compatible data.

Entry points
------------
research_topic(topic, depth, model) -> dict
    Returns a fully-populated dict matching the dossier ReportInput schema.
    Uses the Anthropic web_search tool to gather live data, then synthesises
    it into structured JSON in one API call.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Literal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_SCHEMA = """
{
  "title": "string",
  "subtitle": "string | null",
  "summary": "2–3 paragraph executive narrative",
  "key_findings": ["string", ...],           // 5–7 items
  "market_size": "$XB (year)",
  "market_growth": "X% CAGR (year range)",
  "market_description": "paragraph",
  "geographic_scope": "string",
  "market_segments": ["Segment — X%", ...],
  "metrics": [
    {
      "label": "string",
      "value": "string",
      "unit": "string | null",
      "change": "string | null",
      "trend": "up | down | neutral",
      "description": "string | null"
    }
  ],                                          // 6–8 KPIs
  "competitors": [
    {
      "name": "string",
      "description": "string",
      "market_share": "string | null",
      "founding_year": "string | null",
      "headquarters": "string | null",
      "key_products": ["string"],
      "strengths": ["string"],
      "weaknesses": ["string"]
    }
  ],                                          // 4–6 companies
  "competitive_summary": "paragraph",
  "swot": {
    "strengths":     ["string"],              // 4–5 each
    "weaknesses":    ["string"],
    "opportunities": ["string"],
    "threats":       ["string"]
  },
  "trends": [
    {
      "title": "string",
      "description": "string",
      "impact": "high | medium | low",
      "timeframe": "string",
      "drivers": ["string"]
    }
  ],                                          // 4–6 trends
  "trends_summary": "paragraph",
  "tables": [
    {
      "title": "string",
      "headers": ["string"],
      "rows": [["string"]],
      "notes": "string | null"
    }
  ],                                          // 1–2 tables with real data
  "recommendations": [
    {
      "title": "string",
      "description": "string",
      "priority": "high | medium | low",
      "timeline": "string",
      "owner": "string | null",
      "expected_outcome": "string | null"
    }
  ],                                          // 4–5 items
  "recommendations_summary": "paragraph",
  "appendix": "methodology and sources note"
}
"""

_SYSTEM_PROMPT = f"""\
You are a strategic market research analyst producing a consulting-grade intelligence brief.

Given a research topic, use web search to gather current, specific, data-driven information, \
then synthesise everything into a single structured JSON object.

Research approach:
1. Search for overall market size, valuation, and growth rate (CAGR)
2. Search for major players, market share, and competitive dynamics
3. Search for key metrics and KPIs cited by analysts (Bloomberg, Gartner, McKinsey, etc.)
4. Search for recent trends, disruptions, and forward-looking forecasts
5. Search for strategic recommendations cited in industry reports

Output rules:
- Return ONLY valid JSON — no markdown fences, no explanation, no preamble
- Use real numbers and named sources — no placeholders like "X%" or "TBD"
- All monetary values must include units ("$47B", "€2.1M")
- All years must be explicit ("2024", "2025E", "2025–2030")
- Strengths/weaknesses/drivers must be specific strings, not nested objects

Target schema:
{_SCHEMA}
"""

_DEPTH_CONFIG = {
    "quick":    {"instruction": "Run 4–6 targeted searches on the most important dimensions.", "max_uses": 6},
    "standard": {"instruction": "Run 10–14 searches covering all schema dimensions thoroughly.", "max_uses": 14},
    "deep":     {"instruction": "Run 20+ searches. Maximise specificity across every field.", "max_uses": 25},
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def research_topic(
    topic: str,
    depth: Literal["quick", "standard", "deep"] = "standard",
    model: str = "claude-sonnet-4-5",
    date: str | None = None,
) -> dict:
    """
    Research a topic using Claude with web search and return a dossier-compatible dict.

    Args:
        topic:  Research topic (e.g. "Global SaaS Market 2025", "Climate Tech VC landscape")
        depth:  "quick" (~6 searches), "standard" (~12), "deep" (~20+)
        model:  Anthropic model ID to use
        date:   Report date label — defaults to current month/year

    Returns:
        Dict matching the dossier ReportInput schema, ready to pass to generate_report().

    Raises:
        ValueError: If the API returns no usable text content.
        json.JSONDecodeError: If Claude's response cannot be parsed as JSON.
    """
    import anthropic

    if date is None:
        date = datetime.now().strftime("%B %Y")

    depth_cfg = _DEPTH_CONFIG[depth]

    user_message = (
        f"Research topic: {topic}\n\n"
        f"Depth instruction: {depth_cfg['instruction']}\n\n"
        f"Report date: {date}\n\n"
        "Search thoroughly across all dimensions, then return the complete JSON object."
    )

    logger.info("Researching '%s' (depth=%s, model=%s) …", topic, depth, model)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": depth_cfg["max_uses"],
            }
        ],
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    # Extract the last text block (the JSON synthesis)
    raw = ""
    for block in reversed(response.content):
        if hasattr(block, "text") and block.text.strip():
            raw = block.text.strip()
            break

    if not raw:
        raise ValueError("Research agent returned no text content.")

    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(raw)

    # Ensure required fields are always set
    data["title"] = data.get("title") or topic
    data["date"] = date

    logger.info(
        "Research complete — %d top-level fields populated, %d tool uses",
        sum(1 for v in data.values() if v is not None),
        sum(1 for b in response.content if getattr(b, "type", "") == "tool_use"),
    )

    return data
