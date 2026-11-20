"""Renderizador HTML.

Consome a AST e produz HTML/CSS. Não altera o documento, não reprograma o
formato: é um adaptador de saída, como qualquer outro renderizador que venha
depois (terminal, canvas, Qt).
"""
from __future__ import annotations

from html import escape

from ..components import table as table_component
from ..core.ast import Node
from ..document.model import Document
from .theme import CSS

TRUE_VALUES = (True, "true", "1", "sim", "yes")


def render_document(
    source: Document | str,
    *,
    title: str | None = None,
    standalone: bool = True,
) -> str:
    """Renderiza um documento (ou texto UMD) como HTML."""
    document = source if isinstance(source, Document) else Document(source)
    body = "\n".join(_block(child, document) for child in document.root.children)
    if not standalone:
        return body
    return _page(title or _document_title(document), body)


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
{CSS}
</style>
</head>
<body>
<main class="umd-document">
{body}
</main>
</body>
</html>
"""


def _document_title(document: Document) -> str:
    for node in document.root.children:
        if node.type == "heading":
            return node.text
    if document.path is not None:
        return document.path.stem
    return "Documento UMD"


# ---------------------------------------------------------------- inline


def _inline_children(node: Node) -> str:
    return "".join(_inline(child) for child in node.children)


def _safe_url(raw: str) -> str:
    cleaned = raw.strip()
    lower = cleaned.lower()
    if lower.startswith(("javascript:", "vbscript:")):
        return "#"
    if lower.startswith("data:") and not lower.startswith("data:image/"):
        return "#"
    return escape(cleaned, quote=True)


def _inline(node: Node) -> str:
    kind = node.type
    if kind == "text":
        return escape(node.text).replace("\n", " ")
    if kind == "strong":
        inner = _inline_children(node) or escape(node.text)
        return f"<strong>{inner}</strong>"
    if kind == "em":
        inner = _inline_children(node) or escape(node.text)
        return f"<em>{inner}</em>"
    if kind == "code":
        return f"<code>{escape(node.text)}</code>"
    if kind == "strike":
        inner = _inline_children(node) or escape(node.text)
        return f"<del>{inner}</del>"
    if kind == "link":
        url = _safe_url(str(node.props.get("url", "")))
        return f'<a href="{url}">{_inline_children(node)}</a>'
    return escape(node.text)


# ---------------------------------------------------------------- blocos


def _block(node: Node, document: Document) -> str:
    kind = node.type
    if kind == "heading":
        level = min(6, max(1, int(node.props.get("level", 1))))
        return f'<h{level} class="umd-heading">{_inline_children(node)}</h{level}>'
    if kind == "paragraph":
        return f"<p>{_inline_children(node)}</p>"
    if kind == "list":
        tag = "ol" if node.meta.get("ordered") else "ul"
        items = "".join(f"<li>{_inline_children(item)}</li>" for item in node.children)
        return f"<{tag}>{items}</{tag}>"
    if kind == "quote":
        return f"<blockquote>{_inline_children(node)}</blockquote>"
    if kind == "code_block":
        lang = str(node.props.get("lang", "")).strip()
        class_attr = f' class="language-{escape(lang, quote=True)}"' if lang else ""
        return f"<pre><code{class_attr}>{escape(node.text)}</code></pre>"
    if kind == "hr":
        return "<hr>"
    if kind == "comment":
        return node.text if node.text.startswith("<!--") else escape(node.text)
    if kind == "component":
        handler = _COMPONENTS.get(node.name)
        if handler is None:
            return _fallback(node, document)
        return handler(node, document)
    return ""


def _attrs(node: Node) -> dict[str, object]:
    return {
        key: (attr.value if attr.value is not None else True)
        for key, attr in node.meta.get("attrs", {}).items()
    }


def _children(node: Node, document: Document) -> str:
    return "\n".join(_block(child, document) for child in node.children)


def _fallback(node: Node, document: Document) -> str:
    return (
        '<div class="umd-fallback">'
        f'<span class="umd-fallback-name">[{escape(node.name)}]</span>'
        f"{_children(node, document)}</div>"
    )


# ------------------------------------------------------------ componentes


def _table(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    rows = table_component.data_rows(node)
    aligns = table_component.alignment(node)

    classes = ["umd-table"]
    if attrs.get("striped", True) not in (False, "false", "0", "nao", "não"):
        classes.append("striped")
    if attrs.get("dense") in TRUE_VALUES:
        classes.append("dense")

    caption = ""
    if attrs.get("title"):
        caption = f"<caption>{escape(str(attrs['title']))}</caption>"

    if not rows:
        return f'<table class="{" ".join(classes)}">{caption}</table>'

    header = rows[0] if rows[0].props.get("header") else None
    body_rows = rows[1:] if header is not None else rows

    thead = ""
    if header is not None:
        cells = "".join(
            f"<th{_align_style(index, aligns)}>{escape(cell.text)}</th>"
            for index, cell in enumerate(header.children)
        )
        thead = f"<thead><tr>{cells}</tr></thead>"

    tbody_rows = []
    for row in body_rows:
        cells = "".join(
            f"<td{_align_style(index, aligns)}>{escape(cell.text)}</td>"
            for index, cell in enumerate(row.children)
        )
        tbody_rows.append(f"<tr>{cells}</tr>")

    tbody = f"<tbody>{''.join(tbody_rows)}</tbody>" if tbody_rows else ""
    return f'<table class="{" ".join(classes)}">{caption}{thead}{tbody}</table>'


def _align_style(index: int, aligns: list[str]) -> str:
    if index < len(aligns) and aligns[index] != "left":
        return f' style="text-align:{aligns[index]}"'
    return ""


def _card(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    tone = str(attrs.get("tone", "neutral"))
    styles = []
    if attrs.get("padding") is not None:
        styles.append(f"padding:{_int(attrs.get('padding'))}px")
    if attrs.get("width") is not None:
        styles.append(f"width:{_int(attrs.get('width'))}px")
    style_attr = f' style="{";".join(styles)}"' if styles else ""
    title = ""
    if attrs.get("title"):
        title = f'<h3 class="umd-card-title">{escape(str(attrs["title"]))}</h3>'
    return (
        f'<section class="umd-card tone-{escape(tone, quote=True)}"{style_attr}>'
        f"{title}{_children(node, document)}</section>"
    )


def _callout(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    tone = str(attrs.get("tone", "info"))
    title = ""
    if attrs.get("title"):
        title = f'<p class="umd-callout-title">{escape(str(attrs["title"]))}</p>'
    return (
        f'<aside class="umd-callout tone-{escape(tone, quote=True)}">'
        f"{title}{_children(node, document)}</aside>"
    )


def _columns(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    gap = _int(attrs.get("gap", 16))
    columns = node.children or []
    styles = [f"gap:{gap}px"]
    if columns and attrs.get("equal", True) not in (False, "false", "0", "nao", "não"):
        styles.append(f"grid-template-columns:repeat({len(columns)}, minmax(0, 1fr))")
    return (
        f'<div class="umd-columns" style="{";".join(styles)}">'
        f"{_children(node, document)}</div>"
    )


def _image(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    source = escape(str(attrs.get("src", "")), quote=True)
    alt = escape(str(attrs.get("alt", "")), quote=True)
    dimensions = ""
    if attrs.get("width") is not None:
        dimensions += f' width="{_int(attrs["width"])}"'
    if attrs.get("height") is not None:
        dimensions += f' height="{_int(attrs["height"])}"'
    caption = ""
    if attrs.get("caption"):
        caption = f"<figcaption>{escape(str(attrs['caption']))}</figcaption>"
    return (
        '<figure class="umd-figure">'
        f'<img src="{source}" alt="{alt}"{dimensions}>'
        f"{caption}</figure>"
    )


def _chart(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    title = escape(str(attrs.get("title", "Benchmark Chart")))
    chart_type = str(attrs.get("type", "bar")).lower()
    lines = [c.text.strip() for c in (node.children or []) if c.text]
    if not lines and node.text:
        lines = [line.strip() for line in node.text.splitlines() if line.strip()]

    parsed = []
    max_val = 10.0
    for line in lines:
        parts = line.split("|")
        lbl = parts[0].strip()
        try:
            val = float(parts[1].strip().replace("%", ""))
        except (IndexError, ValueError):
            val = 50.0
        parsed.append((lbl, val))
        if val > max_val:
            max_val = val

    colors = ["#4a88cc", "#6371c6", "#3ca47a", "#c45b85", "#cf8f41", "#846bb3", "#c65c5c"]

    # PIE / DONUT CHART
    if chart_type == "pie":
        total = sum(v for _, v in parsed) or 1.0
        gradient_stops = []
        legend_items = []
        current_deg = 0.0

        for idx, (lbl, val) in enumerate(parsed):
            color = colors[idx % len(colors)]
            pct = (val / total) * 100.0
            next_deg = current_deg + (pct * 3.6)
            gradient_stops.append(f"{color} {current_deg:.1f}deg {next_deg:.1f}deg")
            current_deg = next_deg

            legend_items.append(
                f'<div class="umd-pie-legend-row">'
                f'<span class="umd-pie-dot" style="background:{color}"></span>'
                f'<span class="umd-pie-legend-lbl">{escape(lbl)}</span>'
                f'<span class="umd-pie-legend-val">{val:g} ({pct:.1f}%)</span>'
                f'</div>'
            )

        conic = ", ".join(gradient_stops) if gradient_stops else "#38bdf8 0deg 360deg"
        return (
            f'<div class="umd-chart umd-pie-chart">'
            f'<div class="umd-chart-title">{title}</div>'
            f'<div class="umd-pie-wrap">'
            f'<div class="umd-pie-visual" style="background: conic-gradient({conic});">'
            f'<div class="umd-pie-hole"></div>'
            f'</div>'
            f'<div class="umd-pie-legend">{"".join(legend_items)}</div>'
            f'</div>'
            f'</div>'
        )

    # VERTICAL COLUMN CHART
    if chart_type in ("column", "bar-vertical"):
        col_items = []
        for idx, (lbl, val) in enumerate(parsed):
            color = colors[idx % len(colors)]
            pct = min(100.0, max(0.0, (val / max_val) * 100.0))
            col_items.append(
                f'<div class="umd-column-item">'
                f'<span class="umd-column-val">{val:g}</span>'
                f'<div class="umd-column-track"><div class="umd-column-fill" style="height:{pct:.1f}%; background:{color}"></div></div>'
                f'<span class="umd-column-lbl">{escape(lbl)}</span>'
                f'</div>'
            )
        return (
            f'<div class="umd-chart umd-column-chart">'
            f'<div class="umd-chart-title">{title}</div>'
            f'<div class="umd-columns-flow">{"".join(col_items)}</div>'
            f'</div>'
        )

    # LINE CHART
    if chart_type == "line":
        points = []
        width = 460
        height = 140
        padding = 24
        eff_w = width - (padding * 2)
        eff_h = height - (padding * 2)
        n = len(parsed)
        for idx, (_, val) in enumerate(parsed):
            x = padding + (idx * (eff_w / max(1, n - 1)))
            y = height - padding - ((val / max_val) * eff_h)
            points.append(f"{x:.1f},{y:.1f}")

        pts_attr = " ".join(points)
        x_labels = "".join(f'<span class="umd-line-lbl">{escape(lbl)}</span>' for lbl, _ in parsed)

        return (
            f'<div class="umd-chart umd-line-chart">'
            f'<div class="umd-chart-title">{title}</div>'
            f'<svg viewBox="0 0 {width} {height}" class="umd-line-svg">'
            f'<polyline fill="none" stroke="#38bdf8" stroke-width="2.5" points="{pts_attr}"/>'
            + "".join(f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="4" fill="#818cf8"/>' for p in points) +
            f'</svg>'
            f'<div class="umd-line-x-labels">{x_labels}</div>'
            f'</div>'
        )

    # DEFAULT: HORIZONTAL BAR CHART
    items_html = []
    for idx, (lbl, val) in enumerate(parsed):
        pct = min(100.0, max(0.0, (val / max_val) * 100.0))
        color = colors[idx % len(colors)]
        items_html.append(
            f'<div class="umd-chart-row">'
            f'<span class="umd-chart-label">{escape(lbl)}</span>'
            f'<div class="umd-chart-track"><div class="umd-chart-bar" style="width:{pct:.1f}%; background:{color}"></div></div>'
            f'<span class="umd-chart-val">{val:g}</span>'
            f'</div>'
        )
    return (
        f'<div class="umd-chart">'
        f'<div class="umd-chart-title">{title}</div>'
        f'{"".join(items_html)}'
        f'</div>'
    )


def _pipeline(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    title = escape(str(attrs.get("title", "Pipeline Flow")))
    raw_lines = [c.text.strip() for c in (node.children or []) if c.text]
    raw_text = " ".join(raw_lines) if raw_lines else (node.text or "")
    if "->" in raw_text:
        steps = [s.strip() for s in raw_text.split("->") if s.strip()]
    else:
        steps = [s.strip() for s in raw_text.splitlines() if s.strip()]
    nodes_html = []
    for idx, step in enumerate(steps):
        nodes_html.append(f'<span class="umd-pipeline-node">{escape(step)}</span>')
        if idx < len(steps) - 1:
            nodes_html.append('<span class="umd-pipeline-arrow">→</span>')
    return (
        f'<div class="umd-pipeline">'
        f'<div class="umd-pipeline-title">{title}</div>'
        f'<div class="umd-pipeline-flow">{"".join(nodes_html)}</div>'
        f'</div>'
    )


def _progress(node: Node, document: Document) -> str:
    attrs = _attrs(node)
    label = escape(str(attrs.get("label", "Progress")))
    val = _int(attrs.get("value", 0))
    mx = _int(attrs.get("max", 100)) or 100
    pct = min(100, max(0, int((val / mx) * 100)))
    return (
        f'<div class="umd-progress-card">'
        f'<div class="umd-progress-header">'
        f'<span class="umd-progress-label">{label}</span>'
        f'<span class="umd-progress-badge">{pct}%</span>'
        f'</div>'
        f'<div class="umd-progress-track"><div class="umd-progress-bar" style="width:{pct}%"></div></div>'
        f'</div>'
    )


def _int(value: object, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


_COMPONENTS = {
    "TABLE": _table,
    "CARD": _card,
    "CALLOUT": _callout,
    "COLUMNS": _columns,
    "IMAGE": _image,
    "CHART": _chart,
    "PIPELINE": _pipeline,
    "PROGRESS": _progress,
}
