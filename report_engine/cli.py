"""CLI entry point for report-engine."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(name)s: %(message)s",
)
logger = logging.getLogger("dossier")


@click.group()
@click.version_option(package_name="dossier")
def cli() -> None:
    """dossier — turn structured research data into consulting-grade PDF reports."""


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default=None, help="Output PDF path (default: <input>.pdf)")
@click.option("--title", default=None, help="Override report title")
@click.option("--no-ai", is_flag=True, default=False, help="Skip LLM section selection; use deterministic ordering")
@click.option("--preview", is_flag=True, default=False, help="Open the PDF after generation (requires a PDF viewer)")
@click.option("--html-only", is_flag=True, default=False, help="Write HTML instead of PDF (useful for debugging)")
def generate(
    input_file: Path,
    output: str | None,
    title: str | None,
    no_ai: bool,
    preview: bool,
    html_only: bool,
) -> None:
    """Generate a PDF report from INPUT_FILE (JSON)."""
    from report_engine.renderer import generate as do_generate, render_html
    from report_engine.schema import ReportInput
    from report_engine.selector import select_sections

    # Load and validate input
    try:
        raw = json.loads(input_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid JSON in {input_file}: {exc}", err=True)
        sys.exit(1)

    if title:
        raw["title"] = title

    try:
        report_data = ReportInput.model_validate(raw)
    except Exception as exc:
        click.echo(f"Error: input validation failed:\n{exc}", err=True)
        sys.exit(1)

    data_dict = report_data.model_dump()

    # Determine output path
    suffix = ".html" if html_only else ".pdf"
    out_path = Path(output) if output else input_file.with_suffix(suffix)

    # Select sections
    click.echo(f"Selecting sections ({'AI' if not no_ai else 'deterministic'})…")
    section_ids = select_sections(
        data_dict,
        report_title=data_dict.get("title"),
        use_ai=not no_ai,
    )
    click.echo(f"Sections: {', '.join(section_ids)}")

    # Render
    if html_only:
        html = render_html(section_ids, data_dict)
        out_path.write_text(html, encoding="utf-8")
        click.echo(f"HTML written to: {out_path}")
    else:
        click.echo("Rendering PDF…")
        do_generate(data_dict, section_ids, out_path)
        click.echo(f"PDF written to: {out_path}")

        if preview:
            import os
            os.startfile(str(out_path)) if sys.platform == "win32" else (
                __import__("subprocess").run(["open" if sys.platform == "darwin" else "xdg-open", str(out_path)])
            )


@cli.command(name="list-sections")
def list_sections() -> None:
    """Print all registered sections and their trigger fields."""
    from report_engine.sections import all_sections

    sections = sorted(all_sections(), key=lambda s: s.priority)
    click.echo(f"\n{'ID':<28} {'Priority':<10} {'Triggers when data contains'}")
    click.echo("-" * 80)
    for s in sections:
        fields = ", ".join(s.required_fields)
        click.echo(f"{s.id:<28} {s.priority:<10} {fields}")
    click.echo()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def validate(input_file: Path) -> None:
    """Validate INPUT_FILE and show which sections would be included."""
    from report_engine.schema import ReportInput
    from report_engine.sections import all_sections

    try:
        raw = json.loads(input_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid JSON: {exc}", err=True)
        sys.exit(1)

    try:
        report_data = ReportInput.model_validate(raw)
    except Exception as exc:
        click.echo(f"Validation errors:\n{exc}", err=True)
        sys.exit(1)

    data_dict = report_data.model_dump()
    click.echo(f"\nInput: {input_file}")
    click.echo(f"Title: {data_dict['title']}\n")

    all_secs = sorted(all_sections(), key=lambda s: s.priority)
    included = []
    excluded = []
    for sec in all_secs:
        if sec.is_applicable(data_dict):
            included.append(sec)
        else:
            excluded.append(sec)

    click.echo(f"Sections INCLUDED ({len(included)}):")
    for s in included:
        click.echo(f"  [+] {s.display_name} ({s.id})")

    click.echo(f"\nSections EXCLUDED ({len(excluded)}) — missing required fields:")
    for s in excluded:
        missing = [f for f in s.required_fields if not data_dict.get(f)]
        click.echo(f"  [-] {s.display_name}: needs {', '.join(missing)}")
    click.echo()
