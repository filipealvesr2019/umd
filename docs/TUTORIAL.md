# UI-Markdown (UMD) — Visual Editor User Guide & Tutorial

Welcome to the **UI-Markdown (`.umd`) Visual Editor** tutorial. This guide walks you through everything you need to create, style, and manage rich interactive documents directly inside VS Code or Antigravity IDE — while keeping your files in 100% plain, Git-friendly text.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Working with Text & Typography](#2-working-with-text--typography)
3. [Inserting Components (Context Menu)](#3-inserting-components-context-menu)
4. [Interactive Data Charts](#4-interactive-data-charts)
   - [Comparison Column Chart](#41-comparison-column-chart)
   - [Curved Spline Line Chart](#42-curved-spline-line-chart)
   - [Standard Multi-Series Line Chart](#43-standard-multi-series-line-chart)
   - [Vertical Column Chart](#44-vertical-column-chart)
   - [Horizontal Bar Chart](#45-horizontal-bar-chart)
   - [Pie / Donut Chart](#46-pie--donut-chart)
5. [Layout, Cards, Pipelines & Callouts](#5-layout-cards-pipelines--callouts)
6. [Tables & Checklists](#6-tables--checklists)
7. [Clipboard & Clean Export](#7-clipboard--clean-export)
8. [Keyboard Shortcuts](#8-keyboard-shortcuts)

---

## 1. Getting Started

1. **Install UI-Markdown & the IDE Extension:**
   ```bash
   pip install ui-markdown
   umd install
   ```
2. **Reload your IDE:** Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on macOS) and run **`Developer: Reload Window`**.
3. **Create or open a `.umd` file:** Any file ending in `.umd` opens automatically in the UI-Markdown Visual Editor.
4. **Full Width Toggle:** Click the **`Full Width`** button in the top-right corner of the editor to expand the canvas for wide tables and multi-series charts.

Every edit you make visually is automatically serialized back to clean `.umd` text in real time.

---

## 2. Working with Text & Typography

### Writing & Basic Blocks
- Click anywhere on the canvas and start typing.
- Press **`Enter`** to create a new paragraph block.
- Press **`Backspace`** on an empty block to remove it and jump back to the previous block.
- You can use standard Markdown prefixes or right-click to insert **Headings (H1–H4)**, **Bulleted Lists**, **Numbered Lists**, **Blockquotes**, and **Code Blocks**.

### Floating Text Formatting Toolbar
Highlight **any text inside any element** — including paragraphs, headings, table cells, card bodies, callouts, and chart labels — to summon the floating formatting toolbar:

| Control | Function |
| :--- | :--- |
| **Font** | Switch font family: `Sans`, `Serif`, `Mono`, `Casual`, or `Display`. |
| **Size** | Set exact font size: `11px`, `13px`, `15px`, `18px`, `22px`, `28px`, or `36px`. |
| **Spacing** | Adjust letter spacing (`letter-spacing`): `Normal`, `Tight (-1px)`, `Semi-tight (-0.5px)`, `Semi-wide (+0.5px)`, `Wide (+1px)`, `Wider (+2px)`, `Widest (+3px)`, or `Extra Wide (+5px)`. |
| **Color (`A`)** | Open the color menu with **10 quick palette swatches**, a **Default (`✕`)** reset button, and a native **Custom color...** picker for any hex color. |
| **`B` / `I` / `U` / `S`** | Apply **Bold**, *Italic*, <u>Underline</u>, or ~~Strikethrough~~. |
| **`<>`** | Format selection as `inline code`. |
| **Copy Icon** | Copy the selected text directly to your clipboard. |

> **Tip:** The formatting bar stays open while you combine multiple styles (for example: picking a color, then increasing font size, then adjusting letter spacing) without losing your text selection. Click anywhere outside the toolbar when finished.

---

## 3. Inserting Components (Context Menu)

**Right-click anywhere** on the document canvas to open the Component Context Menu. Components are inserted right after the block you clicked:

- **Clipboard & Formatting**: Copy, Select All, Bold, Italic, Underline, Strikethrough, Inline Code.
- **Text Blocks**: Heading 1–3, Paragraph, Bullet List, Numbered List, Checklist, Quote, Code Block, Divider.
- **Data Charts**:
  - `Comparison Column Chart`
  - `Curved Line Chart`
  - `Line Chart`
  - `Vertical Column Chart`
  - `Horizontal Bar Chart`
  - `Pie / Donut Chart`
- **Visual Blocks**: `Metric Cards Grid`, `Pipeline Architecture`, `Progress Bar`, `Callout Box`, `Table`.

To remove any component block, hover over it and click the **`× Delete`** button in its top-right corner.

---

## 4. Interactive Data Charts

All UMD charts are **directly editable on the canvas** — no raw code editing required.

### 4.1 Comparison Column Chart
Ideal for side-by-side multi-series comparisons (e.g., 2013 vs. 2021, Model A vs. Model B vs. Model C).

- **Add a Comparison Series:** Click **`+ Add Comparison Series`** in the legend bar to add a new colored bar to every group.
- **Rename a Series:** Click any series name in the legend and type directly.
- **Remove a Series:** Hover over a series pill in the legend and click its **`×`** button.
- **Add a Category Group:** Click **`+ Add Group`** at the bottom of the chart.
- **Edit Values:** Click the number directly above any bar and type a new value; all bar heights scale automatically in real time.
- **Edit Group Labels:** Click the category name beneath any group to rename it. Long names truncate cleanly with `...` and reveal their full text on hover.

### 4.2 Curved Spline Line Chart
Smooth Catmull-Rom cubic Bézier curves for trends, trajectories, and time-series data.

- **Add a New Curve:** Click **`+ Add Curve`** in the legend OR click directly on empty space inside the chart canvas.
- **Add a Point to an Existing Curve:** Click directly on any curve line to insert a new data point at that position.
- **Edit or Delete a Point:** Click any circular point marker to open the inline popover, enter a new exact value and click **Save**, or click **Delete** to remove the column/point.
- **Drag Points:** Click and drag any point vertically to adjust its value interactively.
- **Edit X-Axis Labels:** Click any label along the bottom X-axis (e.g., `Jan`, `Epoch 1`) to rename it inline and press **`Enter`**.
- **Rename / Delete Series:** Click series names in the legend to edit, or click `×` on a legend pill to remove a curve.

### 4.3 Standard Multi-Series Line Chart
Works just like the Curved Line Chart with straight point-to-point segments:
- Click the canvas to add a line, click a line to add a point, click a point to edit/delete via popover, drag points vertically, and click X-axis labels to edit them inline.

### 4.4 Vertical Column Chart
Clean, uniform-width vertical columns with horizontal scrolling for large datasets.

- **Add Column:** Click **`+ Add Column`** at the bottom.
- **Edit Values & Labels:** Click the number immediately above a bar to change its value, or click the label below the bar to rename it.
- **Long Labels:** Labels automatically truncate with `...` to keep all bars identical in width; hover over any truncated label to read the full name in a floating tooltip.
- **Delete Column:** Hover over a column and click the small **`×`** button above its value.

### 4.5 Horizontal Bar Chart
Great for ranked benchmarks and scoreboards.
- Click **`+ Add Row`** to append a new entry.
- Edit labels and numeric scores inline; bar widths recalculate proportionally.

### 4.6 Pie / Donut Chart
Great for proportions, budgets, and dataset mixtures.
- Click **`+ Add Slice`** to add a new segment.
- Edit slice names and numeric values in the interactive legend; percentages and SVG arcs update immediately.

---

## 5. Layout, Cards, Pipelines & Callouts

- **Metric Cards Grid (`[COLUMNS]` + `[CARD]`):** Click any card title or metric value to edit inline. Use the controls to add or remove cards side-by-side.
- **AI / Workflow Pipeline (`[PIPELINE]`):** Click any node label to rename a stage, click **`+ Add Step`** to append a stage to the flow, or delete individual steps.
- **Progress Bar (`[PROGRESS]`):** Click the label or percentage value to update progress; the progress bar fills smoothly.
- **Callout Box (`[CALLOUT]`):** Click the title or body text to edit. Supports visual tones (`info`, `success`, `warning`, `danger`, `note`).

---

## 6. Tables & Checklists

### Tables
- Click any header or cell to type and format text.
- Select a table to reveal row/column controls to **add rows**, **add columns**, or **remove** them.

### Checklists
- Click checkboxes directly to toggle tasks between completed (`[x]`) and pending (`[ ]`).
- Press **`Enter`** at the end of a checklist item to automatically create the next checkbox item.

---

## 7. Clipboard & Clean Export

When you copy content from the UMD visual editor (`Ctrl + C` or right-click → **Copy**):
- UMD automatically strips out editor-only buttons (`× Delete`, `+ Add Row`, etc.) and exports clean HTML + plain text.
- Pasting into **Google Docs**, **Microsoft Word**, **Excel/Sheets**, or **Slack/Discord** preserves headings, formatting, tables, and structured chart data cleanly.

To export a standalone webpage from the command line:
```bash
umd render my_document.umd -o my_document.html
```

---

## 8. Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + B` / `Cmd + B` | Bold selected text |
| `Ctrl + I` / `Cmd + I` | Italicize selected text |
| `Ctrl + U` / `Cmd + U` | Underline selected text |
| `Ctrl + A` / `Cmd + A` | Select entire document cleanly |
| `Ctrl + C` / `Cmd + C` | Clean copy (strips editor UI controls) |
| `Right-Click` | Open Component & Formatting Context Menu |
| `Escape` | Close context menu, popovers, or floating toolbar |
| `Enter` | Create new block / commit inline chart label edit |
