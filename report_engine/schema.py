from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class SWOTData(BaseModel):
    strengths: list[str] = []
    weaknesses: list[str] = []
    opportunities: list[str] = []
    threats: list[str] = []


class MetricData(BaseModel):
    label: str
    value: str
    unit: Optional[str] = None
    change: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "neutral"
    description: Optional[str] = None


class CompetitorData(BaseModel):
    name: str
    description: Optional[str] = None
    market_share: Optional[str] = None
    founding_year: Optional[str] = None
    headquarters: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    key_products: Optional[list[str]] = None


class TableData(BaseModel):
    title: str
    headers: list[str]
    rows: list[list[Any]]
    notes: Optional[str] = None


class TrendData(BaseModel):
    title: str
    description: str
    impact: Optional[str] = None  # "high", "medium", "low"
    timeframe: Optional[str] = None
    drivers: Optional[list[str]] = None


class RecommendationData(BaseModel):
    title: str
    description: str
    priority: Optional[str] = None  # "high", "medium", "low"
    timeline: Optional[str] = None
    owner: Optional[str] = None
    expected_outcome: Optional[str] = None


class ReportInput(BaseModel):
    title: str
    date: Optional[str] = None
    subtitle: Optional[str] = None
    author: Optional[str] = None
    client: Optional[str] = None
    confidentiality: Optional[str] = None  # e.g. "CONFIDENTIAL"

    # Executive Summary
    summary: Optional[str] = None
    key_findings: Optional[list[str]] = None

    # Market Overview
    market_size: Optional[str] = None
    market_growth: Optional[str] = None
    market_description: Optional[str] = None
    market_segments: Optional[list[str]] = None
    geographic_scope: Optional[str] = None

    # Competitive Landscape
    competitors: Optional[list[CompetitorData]] = None
    competitive_summary: Optional[str] = None

    # SWOT
    swot: Optional[SWOTData] = None

    # Data Tables
    tables: Optional[list[TableData]] = None

    # Key Metrics
    metrics: Optional[list[MetricData]] = None

    # Trend Analysis
    trends: Optional[list[TrendData]] = None
    trends_summary: Optional[str] = None

    # Recommendations
    recommendations: Optional[list[RecommendationData]] = None
    recommendations_summary: Optional[str] = None

    # Appendix
    appendix: Optional[str] = None
    raw_data: Optional[dict[str, Any]] = None
