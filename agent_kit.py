"""AI-Agent toolkit for UI-Markdown (.umd): compact spec, global SKILL installer,
structured diagnostics hints, and surgical document editing helpers.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from .document.persistence import open_document

UMD_SPEC = """# UI-Markdown (.umd) — Compact Reference for AI Agents

A `.umd` file is pure plain text combining standard Markdown with visual UI components.

## Components

1. Metric Cards Grid:
```umd
[COLUMNS gap="16"]
[CARD title="METRIC NAME"]
92.4%
[/CARD]
[CARD title="LATENCY"]
14.2 ms
[/CARD]
[/COLUMNS]
```

2. Charts (`type`: `bar` | `column` | `pie` | `line` | `curved` | `comparison`):
```umd
[CHART title="Benchmark Scores (%)" type="bar"]
Model A | 88.5
Model B | 92.4
[/CHART]
```
Multi-series (`line`, `curved`, `comparison`) use a `SERIES:` header line:
```umd
[CHART title="Accuracy by Regime (%)" type="comparison"]
SERIES: Exp 131 | Exp 132
TRAIN | 82.0 | 90.0
HELD | 62.5 | 75.0
[/CHART]
```

3. Pipeline Flow:
```umd
[PIPELINE title="Inference Pipeline"]
Input -> Tokenizer -> Attention -> Verifier -> Output
[/PIPELINE]
```

4. Progress Bar (self-closing):
```umd
[PROGRESS label="Training Stage 2" value="94" max="100" /]
```

5. Callout (`tone`: `info` | `success` | `warning` | `danger` | `neutral`):
```umd
[CALLOUT tone="warning" title="Diagnostic"]
Key finding goes here.
[/CALLOUT]
```

6. Tables, Toggles, Checklists, Images & Code/Text Blocks:
- Standard Markdown pipe tables (`| Col A | Col B |` + `| --- | --- |`).
- Toggle lists:
```umd
<details>
<summary>Technical Details</summary>
Hidden details go here.
</details>
```
- Checklists: `- [x] Done` / `- [ ] Pending` (or `[TASKS title="..."]...[/TASKS]`).
- Images: `[IMAGE src="https://..." alt="Plot" caption="Fig 1" width="640" /]`
- Plain text transcripts wrap automatically in ```` ```text ```` blocks.
- Code blocks support syntax highlighting (`python`, `json`, `html`, `js`, `sql`, `bash`).
- Inline typography: `**bold**`, `*italic*`, `<u>underline</u>`, `~~strike~~`, `` `code` ``, and `<span style="color:#ef4444;font-size:18px;font-family:...;letter-spacing:1px">styled</span>`.

## Rules
- Always close `[COLUMNS]`, `[CARD]`, `[CHART]`, `[PIPELINE]`, `[CALLOUT]`, `[TASKS]`, `<details>`.
- Chart values must be plain numbers (use `.` for decimals, e.g. `84.6`, not `84,6%`).
- Escape literal `|` inside table cells as `\\|`.

## CLI & Python Helpers
- Validate: `umd check report.umd --json`
- Inspect structure: `umd outline report.umd --json`
- Surgical edits:
  - `umd add-row report.umd --table 1 --values "Seed 133|HELD|88.0%" --write`
  - `umd set-metric report.umd --label "LATENCY" --value "12.1 ms" --write`
  - `umd append-chart report.umd --chart 1 --values "Exp 133|91.5" --write`
- Python report generator (covers ALL editor elements & text styles):
  ```python
  from umd.builder import Report, styled, bold, italic, underline, strike, inline_code
  r = (
      Report("Title")
      .p(styled("Status: PASS", color="#10b981", bold=True))
      .cards([("Score", "92.4%")])
      .comparison_chart("Bench", [("TRAIN", [82, 90])], series=["Old", "New"])
      .bar_chart("Bars", [("A", 88.5)])
      .column_chart("Cols", [("2k", 14.2)])
      .pie_chart("Mix", [("Code", 35), ("Web", 65)])
      .line_chart("Loss", [("E1", [0.8, 0.7])], series=["Train", "Val"])
      .curved_chart("Curve", [("E1", [1.0, 0.6])], series=["A", "B"])
      .pipeline(["Input", "Model", "Output"])
      .progress("Stage 2", 90)
      .table(["Seed", "Score"], [["130", "84.6%"]])
      .toggle("Details", "Hidden notes")
      .code("plain text...", lang="text")
      .callout("Key finding", tone="warning", title="Note")
      .save("out.umd")
  )
  ```
"""

SKILL_MD = """---
name: umd
description: Create, validate, inspect, and surgically edit UI-Markdown (.umd) visual reports using clean syntax, CLI tools (`umd check`, `umd outline`, `umd add-row`, `umd set-metric`, `umd append-chart`), or the Python `umd.builder.Report` helper.
---

# UI-Markdown (.umd) Authoring & Editing Skill

Use this skill whenever creating, updating, or validating `.umd` visual documents and experiment reports.

## Workflow
1. **Prefer `from umd.builder import Report`** when a Python script generates experiment/benchmark reports — guarantees valid syntax with zero manual formatting.
2. **When editing an existing large `.umd` file**, inspect its structure first with `umd outline <file.umd> --json` instead of reading the entire file, or apply targeted updates with:
   - `umd add-row <file.umd> --table 1 --values "col1|col2|col3" --write`
   - `umd set-metric <file.umd> --label "METRIC" --value "95.0%" --write`
   - `umd append-chart <file.umd> --chart 1 --values "Run 4|95.0" --write`
3. **Always validate after writing**: run `umd check <file.umd> --json` and fix any reported errors before finishing.

---

""" + UMD_SPEC


_DIAGNOSTIC_HINTS = {
    "E_UNKNOWN_COMPONENT": "Use um componente válido: CARD, CALLOUT, COLUMNS, CHART, PIPELINE, PROGRESS, TABLE, TASKS, IMAGE.",
    "E_UNCLOSED_COMPONENT": "Adicione a tag de fechamento correspondente (ex: [/CHART], [/CARD], [/COLUMNS], [/CALLOUT]).",
    "E_STRAY_CLOSE": "Remova a tag de fechamento sobrando ou adicione a tag de abertura correspondente.",
    "E_UNCLOSED_FENCE": "Feche o bloco de código com ``` ou ~~~.",
    "E_COLUMN_COUNT": "Ajuste o número de colunas separadas por '|' para coincidir com o cabeçalho da tabela.",
    "E_CHART_ROW_FORMAT": "Use o formato 'Rótulo | Valor' (ou 'SERIES: S1 | S2' para gráficos multi-série).",
    "E_CHART_NON_NUMERIC": "Use apenas números com ponto decimal nos valores de gráfico (ex: 84.6 em vez de '84,6%').",
    "E_INVALID_PROP": "Verifique os valores permitidos do atributo (use `umd spec` para consultar).",
    "E_REQUIRED_PROP": "Adicione o atributo obrigatório na tag de abertura do componente.",
    "W_EMPTY_CALLOUT": "Adicione texto dentro do bloco [CALLOUT]...[/CALLOUT].",
    "W_EMPTY_CHART": "Adicione ao menos uma linha 'Rótulo | Valor' dentro de [CHART]...[/CHART].",
}


def diagnostic_hint(code: str) -> str:
    return _DIAGNOSTIC_HINTS.get(code, "Consulte `umd spec` para verificar a sintaxe esperada.")


def get_skill_target_directories() -> list[Path]:
    home = Path.home()
    return [
        home / ".gemini" / "antigravity" / "skills" / "umd",
        home / ".claude" / "skills" / "umd",
        home / ".cursor" / "skills" / "umd",
    ]


def install_skill(custom_dir: str | Path | None = None) -> list[Path]:
    targets = [Path(custom_dir)] if custom_dir else get_skill_target_directories()
    written: list[Path] = []
    for folder in targets:
        folder.mkdir(parents=True, exist_ok=True)
        skill_path = folder / "SKILL.md"
        skill_path.write_text(SKILL_MD, encoding="utf-8")
        written.append(skill_path)
    return written


# -- Outline (headings + components + markdown tables) ------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_MD_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")
_ATTR_RE = re.compile(r'([a-zA-Z_][\w-]*)\s*=\s*"([^"]*)"')


def build_outline(path: str | Path) -> dict:
    doc = open_document(path)
    text = doc.source()
    lines = text.splitlines()

    items: list[dict] = []
    table_idx = 0
    chart_idx = 0
    card_idx = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip fenced code blocks
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            lang = stripped[3:].strip() or "text"
            start_line = i + 1
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence):
                i += 1
            items.append({
                "kind": "code",
                "lang": lang,
                "line": start_line,
                "end_line": min(i + 1, len(lines)),
            })
            i += 1
            continue

        # Headings
        hm = _HEADING_RE.match(stripped)
        if hm:
            items.append({
                "kind": f"h{len(hm.group(1))}",
                "line": i + 1,
                "title": hm.group(2).strip(),
            })
            i += 1
            continue

        # Markdown pipe table
        if "|" in stripped and i + 1 < len(lines) and _MD_TABLE_SEP_RE.match(lines[i + 1]):
            table_idx += 1
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            start_line = i + 1
            i += 2
            row_count = 0
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                row_count += 1
                i += 1
            items.append({
                "kind": "table",
                "index": table_idx,
                "line": start_line,
                "end_line": i,
                "headers": headers,
                "rows": row_count,
            })
            continue

        # Toggle list (<details><summary>...</summary>)
        if stripped.lower().startswith("<details"):
            start_line = i + 1
            summary_title = ""
            j = i + 1
            while j < len(lines) and not lines[j].strip().lower().startswith("</details>"):
                sm = re.search(r"<summary>(.*?)</summary>", lines[j], re.IGNORECASE)
                if sm and not summary_title:
                    summary_title = sm.group(1).strip()
                j += 1
            items.append({
                "kind": "toggle",
                "line": start_line,
                "end_line": min(j + 1, len(lines)),
                "title": summary_title,
            })
            i = j + 1
            continue

        # UMD component opening tags
        cm = re.match(
            r"^\[(CHART|CARD|CALLOUT|PIPELINE|PROGRESS|TABLE|COLUMNS|IMAGE|TASKS)\b([^\]]*)\]",
            stripped,
            re.IGNORECASE,
        )
        if cm:
            cname = cm.group(1).upper()
            attrs = dict(_ATTR_RE.findall(cm.group(2)))
            entry: dict = {"kind": cname.lower(), "line": i + 1}
            if cname == "CHART":
                chart_idx += 1
                entry["index"] = chart_idx
                entry["title"] = attrs.get("title", "")
                entry["chart_type"] = attrs.get("type", "bar")
            elif cname == "CARD":
                card_idx += 1
                entry["index"] = card_idx
                entry["title"] = attrs.get("title", "")
                if i + 1 < len(lines) and not lines[i + 1].strip().startswith("[/CARD]"):
                    entry["value"] = lines[i + 1].strip()
            elif cname == "PROGRESS":
                entry["label"] = attrs.get("label", "")
                entry["value"] = attrs.get("value", "")
                entry["max"] = attrs.get("max", "100")
            elif cname == "TABLE":
                table_idx += 1
                entry["index"] = table_idx
            elif cname == "IMAGE":
                entry["src"] = attrs.get("src", "")
                if "caption" in attrs:
                    entry["title"] = attrs["caption"]
                elif "alt" in attrs:
                    entry["title"] = attrs["alt"]
            else:
                if "title" in attrs:
                    entry["title"] = attrs["title"]
                if "tone" in attrs:
                    entry["tone"] = attrs["tone"]
            items.append(entry)

        i += 1

    return {
        "file": str(doc.path),
        "valid": doc.valid,
        "lines": len(lines),
        "items": items,
    }


# -- Surgical Edits -----------------------------------------------------------

def _parse_values(values: Sequence[str]) -> list[str]:
    if len(values) == 1 and "|" in values[0]:
        return [v.strip() for v in values[0].split("|")]
    return [v.strip() for v in values]


def add_table_row(
    path: str | Path,
    table_selector: str | int,
    values: Sequence[str],
    *,
    write: bool = False,
) -> tuple[bool, str, str]:
    """Appends a row to either a [TABLE] component or a Markdown pipe table."""
    target_path = Path(path)
    vals = _parse_values(values)
    sel = str(table_selector).strip().lower()
    if sel.startswith("table#"):
        target_idx = int(sel.split("#", 1)[1])
    else:
        target_idx = int(sel)

    # First check if it's a [TABLE] component via Document
    doc = open_document(target_path)
    if doc.tables() and 1 <= target_idx <= len(doc.tables()):
        table_id = doc.tables()[target_idx - 1].id
        res = doc.append_row(table_id, vals)
        if not res.ok:
            return False, res.message, doc.source()
        if write:
            doc.save()
        return True, res.message, doc.source()

    # Otherwise find Markdown pipe table by 1-based index
    text = target_path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    found = 0
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if "|" in stripped and i + 1 < len(lines) and _MD_TABLE_SEP_RE.match(lines[i + 1]):
            found += 1
            headers = [c.strip() for c in stripped.strip("|").split("|")]
            j = i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                j += 1
            if found == target_idx:
                if len(vals) != len(headers):
                    return (
                        False,
                        f"tabela #{target_idx} espera {len(headers)} colunas, recebeu {len(vals)}",
                        text,
                    )
                escaped = [v.replace("|", r"\|") for v in vals]
                new_row = "| " + " | ".join(escaped) + " |"
                lines.insert(j, new_row)
                updated = newline.join(lines) + (newline if text.endswith("\n") else "")
                if write:
                    target_path.write_text(updated, encoding="utf-8")
                return True, f"linha adicionada à tabela #{target_idx}", updated
            i = j
            continue
        i += 1

    return False, f"tabela #{target_idx} não encontrada em {target_path}", text


def set_metric(
    path: str | Path,
    label: str,
    value: str,
    *,
    subtitle: str | None = None,
    write: bool = False,
) -> tuple[bool, str, str]:
    """Surgically updates a [CARD title="..."] or [PROGRESS label="..."] value."""
    target_path = Path(path)
    text = target_path.read_text(encoding="utf-8")
    target_lower = label.strip().lower()

    # 1. Try [CARD title="..."] ... [/CARD]
    card_pat = re.compile(
        r'(\[CARD\b[^\]]*title="([^"]*)"[^\]]*\]\r?\n)([\s\S]*?)(\r?\n\[/CARD\])',
        re.IGNORECASE,
    )
    for m in card_pat.finditer(text):
        if m.group(2).strip().lower() == target_lower:
            new_body = str(value).strip()
            if subtitle is not None:
                new_body += "\n" + str(subtitle).strip()
            updated = text[: m.start(3)] + new_body + text[m.end(3) :]
            if write:
                target_path.write_text(updated, encoding="utf-8")
            return True, f'métrica [CARD title="{m.group(2)}"] atualizada para {value!r}', updated

    # 2. Try [PROGRESS label="..." value="..." ...]
    prog_pat = re.compile(r'\[PROGRESS\b([^\]]*)/?\]', re.IGNORECASE)
    for m in prog_pat.finditer(text):
        attrs = dict(_ATTR_RE.findall(m.group(1)))
        if attrs.get("label", "").strip().lower() == target_lower:
            old_tag = m.group(0)
            if re.search(r'value="[^"]*"', old_tag):
                new_tag = re.sub(r'value="[^"]*"', f'value="{value}"', old_tag, count=1)
            else:
                new_tag = old_tag[:-2] + f' value="{value}" /]'
            updated = text[: m.start()] + new_tag + text[m.end() :]
            if write:
                target_path.write_text(updated, encoding="utf-8")
            return True, f'progresso [PROGRESS label="{attrs.get("label")}"] atualizado para {value!r}', updated

    return False, f"métrica ou progresso {label!r} não encontrado em {target_path}", text


def append_chart_row(
    path: str | Path,
    chart_selector: str | int,
    values: Sequence[str],
    *,
    write: bool = False,
) -> tuple[bool, str, str]:
    """Appends a data row (`Label | val1 | ...`) to a [CHART] block."""
    target_path = Path(path)
    text = target_path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    vals = _parse_values(values)
    if len(vals) < 2:
        return False, "esperado ao menos 'Rótulo | Valor' (2+ campos)", text

    sel_str = str(chart_selector).strip()
    target_idx: int | None = None
    if sel_str.isdigit():
        target_idx = int(sel_str)
    elif sel_str.lower().startswith("chart#") and sel_str.split("#", 1)[1].isdigit():
        target_idx = int(sel_str.split("#", 1)[1])

    chart_pat = re.compile(
        r'(\[CHART\b([^\]]*)\]\r?\n)([\s\S]*?)(\r?\n?\[/CHART\])',
        re.IGNORECASE,
    )
    matches = list(chart_pat.finditer(text))
    chosen = None
    for idx, m in enumerate(matches, start=1):
        attrs = dict(_ATTR_RE.findall(m.group(2)))
        title = attrs.get("title", "")
        if target_idx is not None and idx == target_idx:
            chosen = (idx, title, m)
            break
        if target_idx is None and sel_str.lower() in title.lower():
            chosen = (idx, title, m)
            break

    if chosen is None:
        return False, f"gráfico {chart_selector!r} não encontrado em {target_path}", text

    idx, title, m = chosen
    row_line = " | ".join(vals)
    body = m.group(3).rstrip("\r\n")
    new_body = (body + newline + row_line) if body else row_line
    updated = text[: m.start(3)] + new_body + newline + "[/CHART]" + text[m.end() :]
    if write:
        target_path.write_text(updated, encoding="utf-8")
    return True, f"linha adicionada ao gráfico #{idx} ({title or 'sem título'}): {row_line}", updated
