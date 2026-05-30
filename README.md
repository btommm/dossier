# dossier

> Turn structured research data into consulting-grade PDF reports — in one command.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Powered by Claude](https://img.shields.io/badge/powered%20by-Claude-orange)

Dossier is a Python CLI tool that takes a JSON file of research data and compiles it into a polished, McKinsey-style PDF report. Claude selects and orders the sections for narrative coherence. WeasyPrint renders the result to a print-ready A4 PDF.

```bash
# One command: research a topic and generate the PDF
dossier run "Global fintech market 2025" --output fintech.pdf

# Or step by step
dossier research "Global fintech market 2025" --output data.json
dossier generate data.json --output fintech.pdf
```

It's also designed as a **v1 building block** — the core logic is cleanly separated so the same engine can be called from a script, an agent pipeline, or an MCP tool with no changes.

---

## What it produces

A multi-section consulting report with:

- **Navy cover page** with title, client, author, date, and confidentiality badge
- **Executive Summary** with narrative and key findings callout box
- **Market Overview** with stat cards for size, growth rate, and segments
- **Key Metrics** displayed as a 3-across KPI card grid
- **Competitive Landscape** with per-competitor profiles, strengths/weaknesses
- **SWOT Analysis** in a color-coded 2×2 grid
- **Trend Analysis** with HIGH / MEDIUM / LOW impact badges
- **Data Tables** with alternating row shading and bold headers
- **Recommendations** numbered with priority, owner, and expected outcome
- **Appendix** with supporting notes and raw data

---

## How it works

```
Topic string  ──►  Claude + web search  ──►  structured JSON
                   (research.py)              (dossier schema)
                                                    │
                                                    ▼
                                         Pydantic validation
                                                    │
                                                    ▼
                                         AI section selector      ← --no-ai: priority sort
                                         (Claude, selector.py)
                                                    │
                                                    ▼
                                         Jinja2 HTML templates
                                         (one per section)
                                                    │
                                                    ▼
                                         CSS assembly
                                         (consulting stylesheet)
                                                    │
                                                    ▼
                                         WeasyPrint → PDF         ← Windows: xhtml2pdf fallback
```

You can enter the pipeline at any stage — `dossier run` starts at the top, `dossier generate` starts at validation.

Each section is a self-contained plugin: a Python class that declares what data fields it needs, plus a Jinja2 template. Adding a new section means adding one `.py` file and one `.html.j2` template — nothing else to change.

---

## Quick start

### 1. Install system dependencies

WeasyPrint requires GTK/Pango native libraries.

**Linux (Debian / Ubuntu)**
```bash
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
    libfontconfig1 libcairo2 libgdk-pixbuf2.0-0 fonts-liberation
```

**macOS**
```bash
brew install pango cairo gdk-pixbuf libffi
```

**Windows**
Install the [GTK3 Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases). If you skip this, dossier automatically falls back to `xhtml2pdf` (pure Python, no system deps) — install it with `pip install dossier[windows]`.

### 2. Install

```bash
git clone https://github.com/btommm/dossier
cd dossier
pip install -e .

# Windows fallback renderer
pip install -e ".[windows]"
```

### 3. Add your API key

```bash
cp .env.example .env
# set ANTHROPIC_API_KEY in .env
```

### 4. Run

```bash
dossier generate examples/example_input.json
# → examples/example_input.pdf
```

---

## CLI reference

### `dossier run "<topic>"` — research + generate in one step

```
dossier run "Global fintech market 2025" --output fintech.pdf

-o, --output PATH              Output PDF path (default: <slug>.pdf)
--depth [quick|standard|deep]  Research depth — quick (~6 searches),
                                standard (~12), deep (~20+)  [default: standard]
--date TEXT                    Report date label (default: current month/year)
--no-ai                        Skip AI section ordering
--preview                      Open the PDF after generation
--save-json PATH               Also save the research JSON
```

### `dossier research "<topic>"` — research only, save JSON

```
dossier research "Global fintech market 2025" --output data.json

-o, --output PATH              JSON output path (default: <slug>.json)
--depth [quick|standard|deep]  [default: standard]
--date TEXT                    Report date label
```

### `dossier generate <input.json>` — generate PDF from existing JSON

```
-o, --output PATH    Output path (default: <input>.pdf)
--title TEXT         Override the report title
--no-ai              Skip Claude; use deterministic section ordering
--preview            Open the PDF after generation
--html-only          Write HTML instead of PDF (good for CSS iteration)
```

### `dossier list-sections`

Prints every registered section, its priority, and the data fields that trigger it.

### `dossier validate <input.json>`

Shows exactly which sections would be included or excluded for a given input file, with reasons for each exclusion.

---

## Input schema

Every field is optional except `title`. Only sections whose required fields are present will be included — you never get blank sections.

See [`examples/example_input.json`](examples/example_input.json) (EV market, exercises all 10 sections) and [`examples/ai_market_report.json`](examples/ai_market_report.json) (AI market, generated from live research) for fully populated examples.

```jsonc
{
  // Report metadata
  "title": "Report Title",            // required
  "date": "May 2025",
  "subtitle": "Subtitle",
  "author": "Author / Firm",
  "client": "Client Name",
  "confidentiality": "CONFIDENTIAL",

  // Executive Summary  →  triggers: summary OR key_findings
  "summary": "Narrative paragraph...",
  "key_findings": ["Finding 1", "Finding 2"],

  // Market Overview  →  triggers: market_size OR market_growth OR market_description
  "market_size": "$487B",
  "market_growth": "22% CAGR",
  "market_description": "Narrative...",
  "market_segments": ["Segment A — 40%", "Segment B — 30%"],
  "geographic_scope": "Global",

  // Key Metrics  →  triggers: metrics
  "metrics": [
    {
      "label": "Revenue", "value": "$5M",
      "change": "+12% YoY", "trend": "up",  // trend: "up" | "down" | "neutral"
      "description": "Optional context"
    }
  ],

  // Competitive Landscape  →  triggers: competitors
  "competitors": [
    {
      "name": "Acme Corp",
      "description": "...",
      "market_share": "25%",
      "founding_year": "2005",
      "headquarters": "New York, NY",
      "key_products": ["Product A", "Product B"],
      "strengths": ["Strong brand"],
      "weaknesses": ["High costs"]
    }
  ],
  "competitive_summary": "Optional narrative...",

  // SWOT Analysis  →  triggers: swot
  "swot": {
    "strengths": ["..."],
    "weaknesses": ["..."],
    "opportunities": ["..."],
    "threats": ["..."]
  },

  // Trend Analysis  →  triggers: trends
  "trends": [
    {
      "title": "Trend name",
      "description": "...",
      "impact": "high",          // "high" | "medium" | "low"
      "timeframe": "2025–2028",
      "drivers": ["Driver 1", "Driver 2"]
    }
  ],

  // Data Tables  →  triggers: tables
  "tables": [
    {
      "title": "Table Name",
      "headers": ["Col A", "Col B"],
      "rows": [["val1", "val2"]],
      "notes": "Source note..."
    }
  ],

  // Recommendations  →  triggers: recommendations
  "recommendations": [
    {
      "title": "Action item",
      "description": "...",
      "priority": "high",        // "high" | "medium" | "low"
      "timeline": "Q3 2025",
      "owner": "CTO",
      "expected_outcome": "..."
    }
  ],

  // Appendix  →  triggers: appendix OR raw_data
  "appendix": "Supplementary notes...",
  "raw_data": { "Source": "McKinsey 2025" }
}
```

---

## Section registry

| ID | Display name | Priority | Triggers when data contains |
|---|---|---|---|
| `cover_page` | Cover Page | 0 | `title` |
| `executive_summary` | Executive Summary | 10 | `summary` or `key_findings` |
| `market_overview` | Market Overview | 20 | `market_size`, `market_growth`, or `market_description` |
| `key_metrics` | Key Metrics | 25 | `metrics` |
| `competitive_landscape` | Competitive Landscape | 30 | `competitors` |
| `trend_analysis` | Trend Analysis | 35 | `trends` |
| `swot_analysis` | SWOT Analysis | 40 | `swot` |
| `data_tables` | Data Tables | 50 | `tables` |
| `recommendations` | Recommendations | 70 | `recommendations` |
| `appendix` | Appendix | 90 | `appendix` or `raw_data` |

---

## Workflows

**One command** — research a topic and get a PDF:
```bash
dossier run "Global fintech market 2025" --output fintech.pdf
```

**Two steps** — inspect the data before rendering:
```bash
dossier research "Global fintech market 2025" --output data.json
# review / edit data.json
dossier generate data.json --output fintech.pdf
```

**In Python** — chain the two functions directly:
```python
from report_engine.research import research_topic
from report_engine.mcp_tool import generate_report

data   = research_topic("Global fintech market 2025", depth="standard")
result = generate_report(data, output_path="fintech.pdf")
# → {"success": True, "output_path": "fintech.pdf", "sections_used": [...], "error": None}
```

**MCP tool** — expose to any agent via an MCP server:
```python
from report_engine.mcp_tool import research_topic, generate_report
# Both functions are clean stubs ready to register as MCP tools.
# research_topic(topic, depth, date)   → dict
# generate_report(data, output_path)   → {"success", "output_path", "sections_used", "error"}
```

---

## Project structure

```
report_engine/
├── cli.py                      # Click CLI (run / research / generate / validate / list-sections)
├── research.py                 # Claude + web search → dossier-compatible JSON
├── selector.py                 # AI section selector + deterministic fallback
├── renderer.py                 # HTML assembly + WeasyPrint / xhtml2pdf
├── schema.py                   # Pydantic v2 input models
├── mcp_tool.py                 # MCP-ready research_topic() + generate_report() stubs
├── sections/
│   ├── __init__.py             # BaseSection base class + plugin registry
│   ├── cover_page.py           # (one file per section)
│   ├── ...
│   └── templates/
│       ├── cover_page.html.j2  # (one Jinja2 template per section)
│       └── ...
└── styles/
    ├── report.css              # Full consulting stylesheet (WeasyPrint)
    └── report_compat.css       # Simplified stylesheet (xhtml2pdf fallback)
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

The test suite (16 tests) covers section selection logic and full HTML rendering. No API key or WeasyPrint/GTK installation required to run it.

---

## Roadmap

| Version | Feature |
|---|---|
| v1.1 | MCP server wiring (`mcp_server.py` with FastAPI transport) |
| v1.2 | Chart rendering — Matplotlib figures embedded in trend and market sections |
| v2.0 | Custom section templates — drop your own `.html.j2` to override any section |
| v2.1 | Multiple style themes — startup, academic, government |
| v2.2 | Batch generation — `dossier generate *.json --output-dir ./reports/` |

---

## License

MIT
