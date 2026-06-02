"""Section selector — deterministic, priority-based. No API calls."""

from __future__ import annotations


def select_sections(data: dict, **_kwargs) -> list[str]:
    """Return all applicable sections sorted by priority."""
    from report_engine.sections import all_sections

    applicable = [s for s in all_sections() if s.is_applicable(data)]
    applicable.sort(key=lambda s: s.priority)
    return [s.id for s in applicable]
