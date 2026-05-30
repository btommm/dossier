"""Assembles section HTML and renders to PDF via WeasyPrint."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# On Windows, Python 3.8+ doesn't search PATH for DLLs loaded via cffi.
# Register known GTK bin directories so WeasyPrint can find its native libs.
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    # Register all dirs that contain GTK native libs; order matters —
    # Tesseract-OCR ships a newer Pango (1.44+) required by WeasyPrint 54+.
    _GTK_CANDIDATES = [
        Path(r"C:\Program Files\Tesseract-OCR"),          # newer Pango/GLib
        Path(r"C:\Program Files\GTK3-Runtime Win64\bin"),
        Path(r"C:\Program Files\Gtk-Runtime\bin"),
        Path(r"C:\Program Files (x86)\GTK3-Runtime\bin"),
    ]
    for _gtk_bin in _GTK_CANDIDATES:
        if _gtk_bin.exists():
            os.add_dll_directory(str(_gtk_bin))

CSS_PATH = Path(__file__).parent / "styles" / "report.css"
CSS_COMPAT_PATH = Path(__file__).parent / "styles" / "report_compat.css"

_HTML_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
{css}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def render_html(section_ids: list[str], data: dict, compat: bool = False) -> str:
    """Render ordered sections into a full HTML document string."""
    from report_engine.sections import get_section

    parts: list[str] = []
    for sid in section_ids:
        try:
            section_cls = get_section(sid)
            html = section_cls.render(data)
            parts.append(html)
        except Exception:
            logger.exception("Failed to render section '%s' — skipping.", sid)

    css_path = CSS_COMPAT_PATH if compat else CSS_PATH
    css = css_path.read_text(encoding="utf-8")
    body = "\n".join(parts)
    return _HTML_WRAPPER.format(
        title=data.get("title", "Report"),
        css=css,
        body=body,
    )


def render_pdf(html: str, output_path: str | Path, compat_html: str | None = None) -> Path:
    """
    Convert HTML string to a PDF file at output_path.

    Tries WeasyPrint first (best quality, requires GTK); falls back to xhtml2pdf
    (pure-Python, no system libraries) using the compat_html variant if provided.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        return _render_weasyprint(html, output_path)
    except (ImportError, OSError) as exc:
        logger.warning(
            "WeasyPrint unavailable (%s). Falling back to xhtml2pdf. "
            "For best results install the GTK runtime: "
            "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html",
            exc,
        )
        return _render_xhtml2pdf(compat_html if compat_html is not None else html, output_path)


def _render_weasyprint(html: str, output_path: Path) -> Path:
    from weasyprint import HTML  # type: ignore[import]
    HTML(string=html).write_pdf(str(output_path))
    logger.info("PDF written (WeasyPrint) → %s", output_path)
    return output_path


def _render_xhtml2pdf(html: str, output_path: Path) -> Path:
    try:
        from xhtml2pdf import pisa  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError(
            "Neither WeasyPrint nor xhtml2pdf is usable. "
            "Install GTK for WeasyPrint, or: pip install xhtml2pdf"
        ) from exc

    with output_path.open("wb") as fh:
        result = pisa.CreatePDF(html, dest=fh)

    if result.err:
        raise RuntimeError(f"xhtml2pdf reported errors rendering the PDF (err={result.err})")

    logger.info("PDF written (xhtml2pdf fallback) → %s", output_path)
    return output_path


def generate(
    data: dict,
    section_ids: list[str],
    output_path: str | Path,
) -> Path:
    """Render sections to HTML then write PDF. Returns the output path."""
    html = render_html(section_ids, data, compat=False)
    compat_html = render_html(section_ids, data, compat=True)
    return render_pdf(html, output_path, compat_html=compat_html)
