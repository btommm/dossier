from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)


class BaseSection(ABC):
    id: ClassVar[str]
    display_name: ClassVar[str]
    required_fields: ClassVar[list[str]]
    optional_fields: ClassVar[list[str]] = []
    priority: ClassVar[int]

    @classmethod
    def is_applicable(cls, data: dict) -> bool:
        return any(data.get(f) is not None for f in cls.required_fields)

    @classmethod
    def render(cls, data: dict) -> str:
        template = _jinja_env.get_template(f"{cls.id}.html.j2")
        return template.render(**data)


# --- Registry ---

_REGISTRY: dict[str, type[BaseSection]] = {}


def register(cls: type[BaseSection]) -> type[BaseSection]:
    _REGISTRY[cls.id] = cls
    return cls


def get_section(section_id: str) -> type[BaseSection]:
    return _REGISTRY[section_id]


def all_sections() -> list[type[BaseSection]]:
    return list(_REGISTRY.values())


def applicable_sections(data: dict) -> list[type[BaseSection]]:
    return [s for s in all_sections() if s.is_applicable(data)]


# Import all sections to trigger registration
from report_engine.sections import (  # noqa: E402, F401
    cover_page,
    executive_summary,
    market_overview,
    competitive_landscape,
    swot_analysis,
    data_tables,
    key_metrics,
    trend_analysis,
    recommendations,
    appendix,
)
