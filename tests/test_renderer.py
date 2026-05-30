"""Tests for HTML rendering (no WeasyPrint required)."""

import pytest

from report_engine.renderer import render_html
from report_engine.selector import select_sections_deterministic

SAMPLE_DATA = {
    "title": "Test Report",
    "date": "2024-01-01",
    "summary": "This is a summary.",
    "key_findings": ["Finding A", "Finding B"],
    "market_size": "$10B",
    "market_growth": "15% CAGR",
    "market_description": "A large market.",
    "competitors": [
        {
            "name": "Acme Corp",
            "description": "A major player",
            "market_share": "25%",
            "strengths": ["Strong brand"],
            "weaknesses": ["High costs"],
        }
    ],
    "swot": {
        "strengths": ["S1", "S2"],
        "weaknesses": ["W1"],
        "opportunities": ["O1"],
        "threats": ["T1"],
    },
    "metrics": [
        {"label": "Revenue", "value": "$5M", "trend": "up", "change": "+12%"}
    ],
    "trends": [
        {"title": "AI trend", "description": "AI is transforming the industry.", "impact": "high"}
    ],
    "recommendations": [
        {"title": "Invest in AI", "description": "Allocate budget.", "priority": "high"}
    ],
    "tables": [
        {
            "title": "Sample Table",
            "headers": ["Name", "Value"],
            "rows": [["Row 1", "100"], ["Row 2", "200"]],
        }
    ],
    "appendix": "Additional notes.",
    "raw_data": None,
}


def test_render_html_returns_string():
    section_ids = select_sections_deterministic(SAMPLE_DATA)
    html = render_html(section_ids, SAMPLE_DATA)
    assert isinstance(html, str)


def test_render_html_contains_title():
    section_ids = select_sections_deterministic(SAMPLE_DATA)
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Test Report" in html


def test_render_html_contains_all_sections():
    section_ids = select_sections_deterministic(SAMPLE_DATA)
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Executive Summary" in html
    assert "Market Overview" in html
    assert "Competitive Landscape" in html
    assert "SWOT Analysis" in html
    assert "Key Metrics" in html
    assert "Trend Analysis" in html
    assert "Recommendations" in html


def test_render_html_cover_page():
    section_ids = ["cover_page"]
    html = render_html(section_ids, SAMPLE_DATA)
    assert "cover-page" in html
    assert "Test Report" in html


def test_render_html_unknown_section_skipped():
    """Unknown section IDs should be silently skipped."""
    section_ids = ["cover_page", "nonexistent_section"]
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Test Report" in html


def test_render_html_valid_document_structure():
    section_ids = select_sections_deterministic(SAMPLE_DATA)
    html = render_html(section_ids, SAMPLE_DATA)
    assert html.strip().startswith("<!DOCTYPE html>")
    assert "</html>" in html
    assert "<style>" in html


def test_competitor_data_rendered():
    section_ids = ["competitive_landscape"]
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Acme Corp" in html


def test_swot_quadrants_rendered():
    section_ids = ["swot_analysis"]
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Strengths" in html
    assert "Weaknesses" in html
    assert "Opportunities" in html
    assert "Threats" in html


def test_metrics_rendered():
    section_ids = ["key_metrics"]
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Revenue" in html
    assert "$5M" in html


def test_table_rendered():
    section_ids = ["data_tables"]
    html = render_html(section_ids, SAMPLE_DATA)
    assert "Sample Table" in html
    assert "Row 1" in html
