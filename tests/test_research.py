"""Tests for the research module (mocked — no real API calls)."""

import json
import pytest
from unittest.mock import MagicMock, patch


MOCK_RESEARCH_DATA = {
    "title": "Global SaaS Market 2025",
    "date": "May 2025",
    "summary": "The global SaaS market is growing rapidly.",
    "key_findings": ["Market reached $300B in 2024", "Growing at 18% CAGR"],
    "market_size": "$300B (2024)",
    "market_growth": "18% CAGR (2024–2029)",
    "market_description": "Cloud software delivery model.",
    "metrics": [{"label": "Market Size", "value": "$300B", "trend": "up"}],
    "competitors": [{"name": "Salesforce", "description": "CRM leader", "strengths": ["Brand"], "weaknesses": ["Price"]}],
    "swot": {"strengths": ["S1"], "weaknesses": ["W1"], "opportunities": ["O1"], "threats": ["T1"]},
    "trends": [{"title": "AI integration", "description": "AI being added to SaaS.", "impact": "high"}],
    "recommendations": [{"title": "Invest in AI", "description": "Prioritise AI features.", "priority": "high"}],
}


def _make_mock_response(data: dict):
    """Build a mock Anthropic messages response containing JSON text."""
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = json.dumps(data)

    tool_block = MagicMock()
    tool_block.type = "tool_use"

    response = MagicMock()
    response.content = [tool_block, text_block]
    return response


@patch("anthropic.Anthropic")
def test_research_topic_returns_dict(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response(MOCK_RESEARCH_DATA)

    from report_engine.research import research_topic
    result = research_topic("Global SaaS Market 2025", depth="quick")

    assert isinstance(result, dict)
    assert result["title"] == "Global SaaS Market 2025"


@patch("anthropic.Anthropic")
def test_research_topic_sets_date(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response(MOCK_RESEARCH_DATA)

    from report_engine.research import research_topic
    result = research_topic("test topic", date="January 2025")

    assert result["date"] == "January 2025"


@patch("anthropic.Anthropic")
def test_research_topic_strips_code_fences(mock_anthropic_cls):
    """Claude sometimes wraps JSON in markdown code fences."""
    fenced = f"```json\n{json.dumps(MOCK_RESEARCH_DATA)}\n```"

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = fenced
    response = MagicMock()
    response.content = [text_block]

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = response

    from report_engine.research import research_topic
    result = research_topic("test")
    assert isinstance(result, dict)
    assert "title" in result


@patch("anthropic.Anthropic")
def test_research_topic_passes_depth_to_api(mock_anthropic_cls):
    """max_uses in the tool config should reflect the chosen depth."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response(MOCK_RESEARCH_DATA)

    from report_engine.research import research_topic
    research_topic("test topic", depth="deep")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    tool = call_kwargs["tools"][0]
    assert tool["max_uses"] == 25


@patch("anthropic.Anthropic")
def test_research_output_is_valid_dossier_input(mock_anthropic_cls):
    """Research output should pass Pydantic validation."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response(MOCK_RESEARCH_DATA)

    from report_engine.research import research_topic
    from report_engine.schema import ReportInput

    data = research_topic("test topic")
    report = ReportInput.model_validate(data)
    assert report.title == "Global SaaS Market 2025"


@patch("anthropic.Anthropic")
def test_research_no_text_raises(mock_anthropic_cls):
    """If the API returns no text block, raise ValueError."""
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.text = ""

    response = MagicMock()
    response.content = [tool_block]

    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = response

    from report_engine.research import research_topic
    with pytest.raises(ValueError, match="no text content"):
        research_topic("test topic")
