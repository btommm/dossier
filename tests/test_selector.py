"""Tests for the section selector."""

import pytest
from unittest.mock import MagicMock, patch

from report_engine.selector import select_sections_deterministic, select_sections


FULL_DATA = {
    "title": "Test Report",
    "date": "2024-01-01",
    "summary": "A summary.",
    "key_findings": ["Finding 1"],
    "market_size": "$1B",
    "market_growth": "10%",
    "market_description": "A market.",
    "competitors": [{"name": "Acme", "description": "A company"}],
    "swot": {
        "strengths": ["Strong brand"],
        "weaknesses": ["High cost"],
        "opportunities": ["New market"],
        "threats": ["Competition"],
    },
    "tables": [{"title": "T", "headers": ["A", "B"], "rows": [["1", "2"]]}],
    "metrics": [{"label": "Revenue", "value": "$5M"}],
    "trends": [{"title": "Trend 1", "description": "Desc"}],
    "recommendations": [{"title": "Rec 1", "description": "Do this"}],
    "appendix": "Notes here.",
    "raw_data": None,
}

MINIMAL_DATA = {
    "title": "Minimal Report",
    "date": "2024-01-01",
}


def test_deterministic_includes_applicable_sections():
    result = select_sections_deterministic(FULL_DATA)
    assert "cover_page" in result
    assert "executive_summary" in result
    assert "market_overview" in result
    assert "competitive_landscape" in result
    assert "swot_analysis" in result


def test_deterministic_excludes_missing_sections():
    result = select_sections_deterministic(MINIMAL_DATA)
    assert "executive_summary" not in result
    assert "competitive_landscape" not in result
    assert "market_overview" not in result


def test_deterministic_always_includes_cover():
    result = select_sections_deterministic(MINIMAL_DATA)
    assert "cover_page" in result


def test_deterministic_sorted_by_priority():
    result = select_sections_deterministic(FULL_DATA)
    from report_engine.sections import get_section
    priorities = [get_section(sid).priority for sid in result]
    assert priorities == sorted(priorities)


def test_select_sections_no_ai():
    result = select_sections(FULL_DATA, use_ai=False)
    assert isinstance(result, list)
    assert len(result) > 0
    assert "cover_page" in result


def test_select_sections_fallback_on_api_failure():
    """AI failure should silently fall back to deterministic."""
    with patch("report_engine.selector.select_sections_ai", side_effect=Exception("API down")):
        result = select_sections(FULL_DATA, use_ai=True)
    deterministic = select_sections_deterministic(FULL_DATA)
    assert result == deterministic
