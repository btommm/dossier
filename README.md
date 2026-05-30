# dossier

**Turn structured research data into consulting-grade PDF reports — in one command.**

Dossier is a Python CLI tool (and MCP-ready function) that takes a JSON file of research data and intelligently compiles it into a polished, McKinsey-style PDF report. It uses the Anthropic API to select and order sections for narrative coherence, then renders the result with a professional CSS stylesheet via WeasyPrint.

```bash
dossier generate research.json --output report.pdf
```

---

## How it works

```
JSON input  →  AI section selector  →  Jinja2 templates  →  WeasyPrint  →  PDF
```

1. **Schema validation** — Pydantic checks your input and identifies which sections have enough data to render
2. **AI section selection** — Claude analyses your data keys and report title, then returns an ordered list of sections optimised for narrative flow (e.g. market context → competition → SWOT → recommendations)
3. **Template rendering** — each section renders its Jinja2 HTML template with your data
4. **PDF generation** — WeasyPrint converts the assembled HTML + CSS to a paginated A4 PDF with page numbers, consulting typography, and print-ready layout

Pass `--no-ai` to skip the API call and use deterministic priority-based ordering instead.

---

## Sections

| Section | Triggers when input contains |
|---|---|
| Cover page | `title` (always included) |
| Executive Summary | `summary` or `key_findings` |
| Market Overview | `market_size`, `market_growth`, or `market_description` |
| Key Metrics | `metrics` |
| Competitive Landscape | `competitors` |
| Trend Analysis | `trends` |
| SWOT Analysis | `swot` |
| Data Tables | `tables` |
| Recommendations | `recommendations` |
| Appendix | `appendix` or `raw_data` |

---

## Quick start

### 1. Install system dependencies (WeasyPrint requires GTK/Pango)

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
    libfontconfig1 libcairo2 libgdk-pixbuf2.0-0 fonts-liberation
```

**macOS:**
```bash
brew install pango cairo gdk-pixbuf libffi
```

**Windows:** Install [GTK3 Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) then add its `bin/` to PATH. On Windows, dossier automatically falls back to `xhtml2pdf` (no system deps needed) if GTK is unavailable — install it with `pip install dossier[windows]`.

### 2. Install dossier

```bash
pip install -e .
# Windows fallback renderer:
pip install -e ".[windows]"
```

### 3. Configure your API key

```bash
cp .env.example .env
# add your ANTHROPIC_API_KEY to .env
```

### 4. Generate a report

```bash
dossier generate examples/example_input.json
# → examples/example_input.pdf
```

---

## CLI

```
dossier generate <input.json> [OPTIONS]

  Options:
    -o, --output PATH    Output PDF path (default: <input>.pdf)
    --title TEXT         Override the report title
    --no-ai              Skip AI section selection; use deterministic ordering
    --preview            Open the PDF after generation
    --html-only          Write HTML instead of PDF (useful for debugging/styling)

dossier list-sections    Print all sections and their trigger fields
dossier validate <input.json>    Show which sections would be included
```

---

## Input schema

All fields optional except `title`. See [`examples/example_input.json`](examples/example_input.json) for a fully populated example (EV market research).

```jsonc
{
  "title": "Report Title",               // required
  "date": "May 2025",
  "subtitle": "Subtitle",
  "author": "Author / Firm",
  "client": "Client Name",
  "confidentiality": "CONFIDENTIAL",

  "summary": "Narrative paragraph...",
  "key_findings": ["Finding 1", "Finding 2"],

  "market_size": "$487B",
  "market_growth": "22% CAGR",
  "market_description": "Narrative...",
  "market_segments": ["Segment A — 40%", "Segment B — 30%"],
  "geographic_scope": "Global",

  "metrics": [
    { "label": "Revenue", "value": "$5M", "change": "+12% YoY", "trend": "up" }
  ],

  "competitors": [
    {
      "name": "Acme Corp", "description": "...", "market_share": "25%",
      "key_products": ["Product A"], "strengths": ["..."], "weaknesses": ["..."]
    }
  ],

  "swot": {
    "strengths": ["..."], "weaknesses": ["..."],
    "opportunities": ["..."], "threats": ["..."]
  },

  "trends": [
    { "title": "Trend name", "description": "...", "impact": "high", "timeframe": "2025–2028", "drivers": ["..."] }
  ],

  "tables": [
    { "title": "Table Name", "headers": ["Col A", "Col B"], "rows": [["val1", "val2"]] }
  ],

  "recommendations": [
    { "title": "Action", "description": "...", "priority": "high", "timeline": "Q3 2025", "owner": "CTO" }
  ],

  "appendix": "Supplementary notes...",
  "raw_data": { "key": "value" }
}
```

---

## MCP integration

`report_engine/mcp_tool.py` exposes a clean function ready to drop into an MCP server:

```python
from report_engine.mcp_tool import generate_report

result = generate_report(
    data=my_research_dict,
    output_path="/tmp/report.pdf",
    title="Q3 Market Brief",
    use_ai=True,
)
# → {"success": True, "output_path": "...", "sections_used": [...], "error": None}
```

The intended v2 workflow:

```
User: "Generate a market report on enterprise AI"
  → Claude calls generate_report() MCP tool
  → Research agent populates the data dict
  → Dossier renders the PDF
  → File lands in your folder, no manual steps
```

---

## Docker

```bash
docker build -t dossier .

docker run --rm \
  -v "$(pwd)/data:/data" \
  -v "$(pwd)/output:/reports" \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  dossier generate /data/research.json -o /reports/report.pdf
```

---

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

All 16 tests cover section selection logic and HTML rendering — no API key or WeasyPrint required to run the test suite.

---

## Roadmap

- **v1.1** — MCP server wiring (`mcp_server.py` with FastAPI transport)
- **v1.2** — Chart rendering (Matplotlib figures embedded in trend/market sections)
- **v2.0** — Custom section templates (drop your own `.html.j2` to override any section)
- **v2.1** — Multiple style themes (startup, academic, government)
- **v2.2** — Batch generation (`dossier generate *.json --output-dir ./reports/`)
