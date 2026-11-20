# Announcing UI-Markdown (UMD): Interactive Notion-Style Visual Documents in Pure Plain Text

> **Introducing `ui-markdown` (`.umd`)**: The open-source document standard and visual editor that bridges the gap between lightweight Markdown writing and rich, reactive workspace documentation — stored cleanly in a single plain text file.

---

## The Documentation Dilemma

For years, developers, researchers, and technical writers have been stuck between two extremes:

1. **Plain Markdown (`.md`)**:
   - **Pros**: Clean, Git-friendly, diffable, stored in plain text.
   - **Cons**: Visually flat, rigid formatting, cannot embed dynamic cards, pipelines, or benchmark charts without messy HTML hacks or unstable external image links.

2. **Proprietary Workspace Apps (Notion, Coda, Confluence)**:
   - **Pros**: Beautiful drag-and-drop cards, multi-column metrics, and interactive blocks.
   - **Cons**: Locked inside proprietary databases. Exporting produces tangled folders containing auxiliary `.html`, `.json`, and asset companion files that break diffs and Git version control.

---

## Enter UI-Markdown (`.umd`)

**UI-Markdown (UMD)** redefines technical documentation by enforcing three non-negotiable principles:

### 1. Zero Companion Files
Everything — rich stat cards, benchmark bar charts, pie distributions, pipeline flows, alert banners, and interactive tables — lives directly inside a **single `.umd` plain text file**. No companion `.html` files, no hidden metadata caches, no folder dependencies.

### 2. Full Bi-directional Lossless Roundtrip
Unlike superficial previewers, UMD is powered by an AST-backed Python parser and visual editor. Edits made in the visual editor instantly sync back to pure Markdown syntax without reordering nodes, mangling comments, or breaking document structure.

### 3. Built-In AI & Data Graphics
Designed specifically for modern engineering and Artificial Intelligence workflows, UMD includes native visual blocks for:
- **AI Model Pipelines**: Visual workflow stages (`Prompt -> Tokenizer -> Attention -> Tool Router -> Verifier Agent`).
- **Benchmark Charts**: Multi-model comparisons with auto-scaled horizontal bars.
- **Latency & Context Profiles**: Vertical column charts for token throughput and latency.
- **Dataset Mixtures**: Conic-gradient pie and donut distributions with interactive legends.
- **Training & Alignment Progress**: Real-time progress bars for RLVR and fine-tuning checkpoints.

---

## Architectural Deep Dive

### Syntax That Feels Natural

UMD extends CommonMark with clean, bracketed block declarations:

```markdown
# DeepReason-70B: Model Evaluation

[COLUMNS gap="20"]
[CARD title="PARAMETERS"] 70.6 Billion [/CARD]
[CARD title="CONTEXT WINDOW"] 128,000 tokens [/CARD]
[CARD title="TARGET MODALITY"] Multi-Step Reasoning [/CARD]
[/COLUMNS]

## 1. Inference Pipeline

[PIPELINE title="End-to-End Inference Pipeline"]
User Query -> Semantic Tokenizer -> Mixture of Attention Layers -> Streaming Output
[/PIPELINE]

## 2. Benchmark Evaluation

[CHART title="Zero-Shot Reasoning Benchmark Scores (%)" type="bar"]
GPT-4o | 88.5
Claude 3.5 Sonnet | 89.2
DeepReason-70B (Ours) | 92.4
[/CHART]

## 3. Dataset Composition

[CHART title="Pretraining Dataset Mixture (%)" type="pie"]
Code & Repositories | 35
Scientific Papers | 25
Web Curated Text | 20
Mathematical Proofs | 20
[/CHART]
```

### Security-First Architecture

Because UMD documents render to webviews and standalone HTML, security is built into the parser core:
- **XSS Sanitization**: All inline HTML elements are escaped to prevent tag injection.
- **Protocol Neutralization**: Disallowed schemes like `javascript:`, `vbscript:`, and unsafe `data:` links are disarmed to `#`.
- **Attribute Breakout Defense**: All attribute values are strictly escaped against quote escape vulnerabilities.
- **Fuzzing Resiliency**: Unclosed components and malformed syntax produce graceful AST diagnostics without throwing exceptions.

---

## Getting Started

### 1. Installation

Install the package from PyPI:

```bash
pip install ui-markdown
```

### 2. Install Visual Editor in VS Code / Antigravity IDE

Run the installer command:

```bash
umd install
```

Reload your editor (`Ctrl+Shift+P > Developer: Reload Window`). Opening any `.umd` file now launches the visual Notion-like editor automatically!

### 3. CLI Power Tools

```bash
# Export to self-contained production HTML
umd render evaluation.umd -o evaluation.html

# Validate document structure
umd check evaluation.umd

# Open the standalone editor
umd edit evaluation.umd
```

### 4. Python API

```python
from umd import parse, render_document, Document

# Parse document into AST
result = parse(open("ai_model_card.umd", encoding="utf-8").read())

# Generate styled HTML
html = render_document(result)

# Programmatic editing
doc = Document.from_text(open("ai_model_card.umd", encoding="utf-8").read())
doc.append_paragraph("Validated for production rollout.")
```

---

## Open Source & Community

`ui-markdown` is open-sourced under the **MIT License**.

- **Source Code**: [G:\umd](file:///G:/umd)
- **Documentation**: [README.md](file:///G:/umd/README.md)
- **Publishing & Packaging Guide**: [PUBLISHING_GUIDE.md](file:///G:/umd/PUBLISHING_GUIDE.md)

Welcome to the future of technical writing — clean plain text on disk, pure visual fluidity on screen.
