<div align="center">

# UI-Markdown (UMD)

**Interactive Visual Documents in Pure Plain Text**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-75%20passed-brightgreen.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20external-purple.svg)]()
[![Tutorial](https://img.shields.io/badge/docs-Editor%20Tutorial-blue.svg)](docs/TUTORIAL.md)

*Combine fluid Markdown writing with interactive UI blocks, live editable data charts, rich typography controls, and architecture pipelines — stored cleanly in a single `.umd` file with zero companion files.*

[Overview](#-overview) • [Key Features](#-key-features) • **[📖 Editor Tutorials](#-visual-editor-tutorials-all-features)** • [Quick Start](#-quick-start) • [Syntax Reference](#-syntax--component-reference) • [Python API](#-python-api) • [License](#-license)

<br/>

<img src="https://raw.githubusercontent.com/filipealvesr2019/umd/main/assets/screenshot_01_editor_overview.png" alt="UI-Markdown Visual Editor: Stat Cards and Architecture Pipeline" width="900" style="border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);" />

</div>

---

## 🌟 Overview

**UI-Markdown (`.umd`)** bridges the gap between readable plain-text Markdown and rich visual document editors.

Traditional documentation tools often force you to choose between:
1. **Plain Markdown**: Lightweight and Git-friendly, but visually plain with limited interactivity and no structured visual components.
2. **Proprietary Document Apps**: Visually rich, but locked inside proprietary databases or accompanied by messy multi-file bundles (`.html`, `.json`, companion asset folders).

**UMD solves this.** Every document is stored entirely in **pure human-readable text** under the `.umd` extension, with an AST-backed parser guaranteeing **100% lossless roundtrip preservation**.

> 📖 **New to UMD?** Read the complete step-by-step **[Editor User Guide & Tutorial](docs/TUTORIAL.md)** to master every tool, chart, and shortcut.

<div align="center">
  <img src="https://raw.githubusercontent.com/filipealvesr2019/umd/main/assets/screenshot_02_pipeline_cards.png" alt="Inference Pipeline and Benchmark Evaluation" width="880" style="border-radius: 8px; margin: 16px 0;" />
</div>

---

## ✨ Key Features

- **📄 Zero Companion Files**: Everything — styled text, metrics, charts, pipelines, callouts, checklists, and tables — lives inside one plain `.umd` text file.
- **🎨 Interactive Visual Editor**: Seamless WYSIWYG editor built for **Antigravity IDE** and **VS Code**, featuring full keyboard navigation, right-click component insertion menus, and real-time live sync.
- **✍️ Universal Rich Typography Toolbar**: Select any text in any element (paragraphs, headings, tables, cards, callouts, or chart labels) to customize:
  - **Font Family** (`Sans`, `Serif`, `Mono`, `Casual`, `Display`)
  - **Font Size** (`11px` to `36px`)
  - **Letter Spacing** (`-1px` to `+5px`, or `Normal`)
  - **Text Color** (10 quick palette swatches + custom color picker)
  - **Inline Styles** (**Bold**, *Italic*, <u>Underline</u>, ~~Strikethrough~~, `Inline Code`, and quick Copy)
- **🔄 Lossless Bi-Directional Roundtrip**: Visual edits immediately sync back to clean `.umd` Markdown without reordering blocks, mangling comments, or breaking formatting.
- **📊 Interactive Data & AI Charts Built-In**:
  - **Comparison Column Charts (`comparison`)**: Grouped multi-series vertical bars with dynamic `+ Add Comparison Series` and `+ Add Group`, inline value editing, and legend customization.
  - **Curved Spline Line Charts (`curved`)**: Smooth cubic Bézier trajectories where you can click the canvas to add a new curve, click any curve to insert points, drag points vertically, or click points/X-axis labels to edit inline.
  - **Multi-Series Line Charts (`line`)**: Direct SVG plotting with interactive point popovers, drag-to-adjust values, and inline X-axis label editing.
  - **Vertical Column Charts (`column`)**: Uniform-width bars, values anchored directly above each bar, and truncated labels with full-text hover tooltips.
  - **Horizontal Bar Charts (`bar`)**: Benchmark comparisons with proportional bars.
  - **Pie / Donut Charts (`pie`)**: Dataset mixtures and distributions with interactive legends.
- **🧩 Structured Layout & Workflow Blocks**:
  - **AI Pipeline Architecture (`[PIPELINE]`)**: End-to-end step flows (`Input -> Process -> Output`).
  - **Stat Cards & Multi-Column Grids (`[COLUMNS]`, `[CARD]`)**: Responsive metric dashboards.
  - **Progress Bars (`[PROGRESS]`)**: Multi-stage training, project, or milestone tracking.
  - **Callouts (`[CALLOUT]`)**: Styled banners (`info`, `success`, `warning`, `danger`, `note`).
  - **Interactive Checklists & Tables**: Toggleable task lists and editable grids with dynamic row/column controls.
- **📋 Clean Clipboard Export**: Copy content directly into Google Docs, Word, or chat apps without carrying over editor buttons or UI overlays.
- **🛡️ Security-First Core**: Built-in XSS defense, attribute breakout protection, sanitized URLs (`javascript:`/`vbscript:` neutralization), and resilient fuzz handling.
- **⚡ Zero External Dependencies**: Core engine is 100% standard-library Python with lightning-fast execution (<1ms parse time).

---

## 📊 Rich AI & Data Visualizations

### 1. Benchmark Horizontal Bar Charts
Compare LLM benchmarks, evaluation scores, or accuracy metrics with auto-calculated visual bars:

<div align="center">
  <img src="https://raw.githubusercontent.com/filipealvesr2019/umd/main/assets/screenshot_03_benchmark_charts.png" alt="Benchmark Horizontal Bar Chart" width="880" style="border-radius: 8px; margin: 16px 0;" />
</div>

### 2. Vertical Column & Pie / Donut Charts
Visualize latency across context lengths with uniform-width columns, hover tooltips on long labels, and dataset token distributions:

<div align="center">
  <img src="https://raw.githubusercontent.com/filipealvesr2019/umd/main/assets/screenshot_04_pie_column_charts.png" alt="Vertical Column Chart and Pie/Donut Chart" width="880" style="border-radius: 8px; margin: 16px 0;" />
</div>

### 3. Reactive Progress, Callouts & Checklists
Track alignment stages with progress meters, status banners, and interactive task checkboxes:

<div align="center">
  <img src="https://raw.githubusercontent.com/filipealvesr2019/umd/main/assets/screenshot_05_checklist_callouts.png" alt="Progress Cards, Alert Callouts, and Task Checklists" width="880" style="border-radius: 8px; margin: 16px 0;" />
</div>

---

## 🚀 Quick Start

### 1. Installation

Install via pip:

```bash
pip install ui-markdown
```

### 2. Install the IDE Extension

Activate the visual editor in VS Code and Antigravity IDE with a single command:

```bash
umd install
```

> **Tip:** Reload your IDE (`Ctrl+Shift+P` → `Developer: Reload Window`). Click any `.umd` file to open it directly in the visual editor!

---

## 📖 Visual Editor Tutorials (All Features)

Everything in UI-Markdown can be created and edited visually right on the canvas. Explore the quick tutorials below or open the **[Complete Step-by-Step User Guide (`docs/TUTORIAL.md`)](docs/TUTORIAL.md)** for full details.

| Tutorial Topic | What You Will Learn | Direct Link |
| :--- | :--- | :--- |
| **1. Getting Started & Layout** | Installing the IDE extension, opening `.umd` files, and toggling **Full Width** mode | [Read Guide →](docs/TUTORIAL.md#1-getting-started) |
| **2. Typography & Text Styling** | Changing **Font Family**, **Font Size**, **Letter Spacing**, **Text Color** (palette + custom picker), **Bold / Italic / Underline / Strike / Code** on any element | [Read Guide →](docs/TUTORIAL.md#2-working-with-text--typography) |
| **3. Right-Click Component Menu** | Inserting headings (H1–H4), lists, toggles, tables, charts, pipelines, and deleting blocks | [Read Guide →](docs/TUTORIAL.md#3-inserting-components-context-menu) |
| **4. Interactive Data Charts** | Editing Comparison Columns, Curved Spline Lines, Multi-Series Lines, Vertical Columns, Horizontal Bars, and Pie/Donut charts directly on canvas | [Read Guide →](docs/TUTORIAL.md#4-interactive-data-charts) |
| **5. Cards, Pipelines & Callouts** | Building Metric Card grids, AI architecture pipelines, progress meters, and styled callouts | [Read Guide →](docs/TUTORIAL.md#5-layout-cards-pipelines--callouts) |
| **6. Tables, Checklists & Toggles** | Dynamic table rows/columns, interactive to-do checkboxes, collapsible toggle lists, quotes, code blocks, and dividers | [Read Guide →](docs/TUTORIAL.md#6-tables-checklists-toggles--code-blocks) |
| **7. Clean Clipboard Export** | Copying tables, charts, and styled text cleanly into Google Docs, Word, Sheets, or chat apps | [Read Guide →](docs/TUTORIAL.md#7-clipboard--clean-export) |
| **8. Keyboard Shortcuts** | Essential shortcuts for fast visual editing | [Read Guide →](docs/TUTORIAL.md#8-keyboard-shortcuts) |

### Quick How-To Highlights

- **Format Any Text Anywhere:** Select any text (in paragraphs, headings, tables, cards, callouts, or chart labels) to open the floating toolbar. Combine **Font**, **Size**, **Spacing** (`letter-spacing`), **Color** (10 swatches + custom color picker), and **B / I / U / S / `<>`** — the toolbar stays open while you apply multiple styles.
- **Insert Any Block:** **Right-click** anywhere on the canvas to insert headings, lists, checklists, toggle lists, tables, callouts, metric cards, pipelines, progress bars, or any of the 6 interactive chart types.
- **Edit Curved & Line Charts Visually:** Click empty canvas space to add a new curve/line, click directly on any curve to insert a point, click any point to edit/delete its value, drag points vertically, or click X-axis labels to rename them inline.
- **Edit Comparison & Column Charts:** Click **`+ Add Comparison Series`** or **`+ Add Group`** / **`+ Add Column`**, click numbers above bars to edit values in real time, and hover over truncated long labels to view the full name.
- **Copy Cleanly:** Press `Ctrl + C` (or right-click → **Copy**) to copy clean HTML + plain text without editor buttons or UI chrome.

---

## 💻 CLI Commands

The `umd` CLI provides high-performance document tools:

```bash
# Render a .umd document to standalone HTML
umd render document.umd -o document.html

# Validate syntax and check for structural errors
umd check document.umd

# Open the visual editor server
umd edit document.umd

# Re-install or update the IDE extension
umd install
```

---

## 🧩 Syntax & Component Reference

UMD supports all standard CommonMark syntax along with interactive block components and inline typography styles. For a full interactive walkthrough, see **[docs/TUTORIAL.md](docs/TUTORIAL.md)**.

### 1. Comparison Column Chart (Multi-Series Grouped Bars)
```markdown
[CHART title="Population of Selected Countries (Millions)" type="comparison" series="2013, 2021"]
Germany | 80.6 | 83.2
Spain | 46.6 | 47.4
France | 65.8 | 67.7
Italy | 60.2 | 59.1
[/CHART]
```

### 2. Curved Spline Line Chart & Standard Line Chart
```markdown
[CHART title="Metric Trajectory Trends" type="curved" series="Series A, Series B, Series C"]
Jan | 75 | 50 | 48
Mar | 66 | -10 | 22
May | 70 | -18 | 14
Jul | 60 | 2 | 15
Sep | 62 | -12 | 8
[/CHART]

[CHART title="Training vs Validation Loss" type="line" series="Train Loss, Val Loss"]
Epoch 1 | 0.85 | 0.92
Epoch 2 | 0.62 | 0.71
Epoch 3 | 0.45 | 0.58
Epoch 4 | 0.34 | 0.49
[/CHART]
```

### 3. Bar, Column & Pie Charts
```markdown
[CHART title="Zero-Shot Reasoning Benchmark Scores (%)" type="bar"]
GPT-4o | 88.5
Claude 3.5 Sonnet | 89.2
DeepSeek-V3 | 88.8
DeepReason-70B (Ours) | 92.4
[/CHART]

[CHART title="Inference Latency by Context Length (ms)" type="column"]
2k Tokens | 14.2
8k Tokens | 22.8
32k Tokens | 41.5
128k Tokens | 104.3
[/CHART]

[CHART title="Pretraining Dataset Mixture (%)" type="pie"]
Code & Repositories | 35
Scientific Papers | 25
Web Curated Text | 20
Mathematical Proofs | 12
Conversational Dialog | 8
[/CHART]
```

### 4. Architecture Pipelines
```markdown
[PIPELINE title="End-to-End Inference Pipeline"]
User Query -> Semantic Tokenizer -> Mixture of Attention Layers -> Tool Calling Router -> Verifier Agent -> Streaming Output
[/PIPELINE]
```

### 5. Stat Cards & Multi-Column Grids
```markdown
[COLUMNS gap="20"]

[CARD title="PARAMETERS"]
70.6 Billion (Dense Decoder-Only)
[/CARD]

[CARD title="CONTEXT WINDOW"]
128,000 tokens
[/CARD]

[CARD title="TARGET MODALITY"]
Code, Math & Multi-Step Reasoning
[/CARD]

[/COLUMNS]
```

### 6. Reactive Progress, Callouts & Inline Styling
```markdown
[PROGRESS label="Stage 2 Reinforcement Learning (RLVR)" value="94" max="100" /]

[CALLOUT tone="success" title="Verification Passed"]
All unit benchmarks, safety filters, and latency boundaries passed.
[/CALLOUT]

Highlighted text with <span style="color: #ef4444; font-size: 22px; letter-spacing: 2px;">custom typography</span> persists losslessly.
```

---

## 🐍 Python API

Integrate UMD programmatically into your scripts, CI/CD pipelines, or agent workflows:

```python
from umd import parse, render_document, Document

# 1. Parse UMD text into an AST
doc_text = """
# Model Evaluation
[PROGRESS label="Fine-Tuning" value=95 max=100 /]
"""
result = parse(doc_text)
print(f"Parsed {len(result.root.children)} root nodes.")

# 2. Render to self-contained HTML
html_output = render_document(doc_text, standalone=True)
with open("evaluation.html", "w", encoding="utf-8") as f:
    f.write(html_output)

# 3. Document Object Model editing
doc = Document.from_text(doc_text)
doc.append_paragraph("Evaluation completed successfully.")
print(doc.to_text())
```

---

## 🧪 Testing & Verification

UMD includes a comprehensive test suite covering parser grammar, AST validation, roundtrip persistence, security escaping, Playwright visual editor interactions, and rendering:

```bash
pytest tests/
```

**Status:** 75 passed (100% pass rate across editing, interactive charts, typography formatting, parsing, rendering, roundtrip, and security modules).

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full details.
