"""Programmatic Python builder for UI-Markdown (.umd) documents.

Covers every block element and inline text style supported by the UMD Visual Editor,
with zero external dependencies::

    from umd.builder import Report, styled, bold, inline_code

    r = Report("Experiment 132")
    r.p(f"Status: {styled('PASS', color='#10b981', bold=True)} on {inline_code('HELD01')}")
    r.cards([("TRAIN", "18/20", "90.0%"), ("HELD", "6/8", "75.0%")])
    r.comparison_chart("Accuracy (%)", [("TRAIN", [82, 90]), ("HELD", [62.5, 75])], series=["Exp 131", "Exp 132"])
    r.table(["Seed", "Score"], [["130", "84.6%"], ["131", "75.0%"]])
    r.save("relatorio_132.umd")
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Sequence, Union

Number = Union[int, float]

FONT_PRESETS: dict[str, str] = {
    "sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "serif": "Georgia, Cambria, 'Times New Roman', serif",
    "mono": "'JetBrains Mono', Consolas, 'Courier New', monospace",
    "casual": "'Comic Sans MS', 'Segoe Print', cursive",
    "display": "Impact, Haettenschweiler, sans-serif",
}


# -- Inline Text Formatting Helpers ------------------------------------------

def bold(text: object) -> str:
    return f"**{text}**"


def italic(text: object) -> str:
    return f"*{text}*"


def underline(text: object) -> str:
    return f"<u>{text}</u>"


def strike(text: object) -> str:
    return f"~~{text}~~"


def inline_code(text: object) -> str:
    return f"`{text}`"


def styled(
    text: object,
    *,
    color: str | None = None,
    size: Union[int, str, None] = None,
    font: str | None = None,
    spacing: Union[int, float, str, None] = None,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strike: bool = False,
) -> str:
    """Formats inline text using the exact syntax supported by UMD's floating toolbar."""
    out = str(text)
    styles: list[str] = []
    if color:
        styles.append(f"color:{color}")
    if size is not None:
        size_val = f"{size}px" if isinstance(size, (int, float)) else str(size)
        styles.append(f"font-size:{size_val}")
    if font:
        font_val = FONT_PRESETS.get(font.strip().lower(), font)
        styles.append(f"font-family:{font_val}")
    if spacing is not None:
        spacing_val = f"{spacing}px" if isinstance(spacing, (int, float)) else str(spacing)
        styles.append(f"letter-spacing:{spacing_val}")

    if styles:
        css = ";".join(styles).replace('"', "'")
        out = f'<span style="{css}">{out}</span>'
    if underline:
        out = f"<u>{out}</u>"
    if strike:
        out = f"~~{out}~~"
    if italic:
        out = f"*{out}*"
    if bold:
        out = f"**{out}**"
    return out


# -- Internal Escaping Helpers -----------------------------------------------

def _escape_attr(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace('"', "'")


def _escape_cell(value: object) -> str:
    return str(value).replace("\r\n", " ").replace("\n", " ").replace("|", r"\|").strip()


def _format_num(value: object) -> str:
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value).strip()


# -- Document Builder ---------------------------------------------------------

class Report:
    """Fluent builder covering every block element and text style in UMD."""

    def __init__(self, title: str | None = None, subtitle: str | None = None) -> None:
        self._blocks: list[str] = []
        if title:
            self.h1(title)
        if subtitle:
            self.p(subtitle)

    # -- Headings & prose -----------------------------------------------------

    def heading(self, level: int, text: object) -> "Report":
        lvl = max(1, min(6, int(level)))
        self._blocks.append(f"{'#' * lvl} {str(text).strip()}")
        return self

    def h1(self, text: object) -> "Report":
        return self.heading(1, text)

    def h2(self, text: object) -> "Report":
        return self.heading(2, text)

    def h3(self, text: object) -> "Report":
        return self.heading(3, text)

    def h4(self, text: object) -> "Report":
        return self.heading(4, text)

    def p(
        self,
        text: object,
        *,
        color: str | None = None,
        size: Union[int, str, None] = None,
        font: str | None = None,
        spacing: Union[int, float, str, None] = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        strike: bool = False,
    ) -> "Report":
        content = str(text).strip()
        if any((color, size is not None, font, spacing is not None, bold, italic, underline, strike)):
            content = styled(
                content,
                color=color,
                size=size,
                font=font,
                spacing=spacing,
                bold=bold,
                italic=italic,
                underline=underline,
                strike=strike,
            )
        self._blocks.append(content)
        return self

    paragraph = p
    text = p

    def quote(self, text: object) -> "Report":
        lines = [f"> {line}" if line.strip() else ">" for line in str(text).splitlines()]
        self._blocks.append("\n".join(lines))
        return self

    def divider(self) -> "Report":
        self._blocks.append("---")
        return self

    hr = divider

    def raw(self, text: object) -> "Report":
        self._blocks.append(str(text).rstrip())
        return self

    # -- Lists & toggles ------------------------------------------------------

    def bullets(self, items: Sequence[object]) -> "Report":
        lines = [f"- {item}" for item in items]
        if lines:
            self._blocks.append("\n".join(lines))
        return self

    def numbers(self, items: Sequence[object]) -> "Report":
        lines = [f"{idx}. {item}" for idx, item in enumerate(items, start=1)]
        if lines:
            self._blocks.append("\n".join(lines))
        return self

    def checklist(self, items: Sequence[Union[tuple[str, bool], str]]) -> "Report":
        lines: list[str] = []
        for item in items:
            if isinstance(item, tuple):
                label, checked = item[0], bool(item[1])
            else:
                label, checked = str(item), False
            mark = "x" if checked else " "
            lines.append(f"- [{mark}] {label}")
        if lines:
            self._blocks.append("\n".join(lines))
        return self

    todo = checklist

    def toggle(self, summary: object, body: object) -> "Report":
        self._blocks.append(
            f"<details>\n<summary>{str(summary).strip()}</summary>\n{str(body).strip()}\n</details>"
        )
        return self

    # -- Code, media, tables & callouts ---------------------------------------

    def code(self, content: object, lang: str = "text") -> "Report":
        body = str(content).rstrip("\n")
        fence = "~~~" if "```" in body else "```"
        tag = (lang or "text").strip()
        self._blocks.append(f"{fence}{tag}\n{body}\n{fence}")
        return self

    code_block = code

    def image(
        self,
        src: str,
        *,
        alt: str = "",
        caption: str | None = None,
        width: int | None = None,
    ) -> "Report":
        attrs = [f'src="{_escape_attr(src)}"']
        if alt:
            attrs.append(f'alt="{_escape_attr(alt)}"')
        if caption:
            attrs.append(f'caption="{_escape_attr(caption)}"')
        if width is not None:
            attrs.append(f'width="{int(width)}"')
        self._blocks.append(f"[IMAGE {' '.join(attrs)} /]")
        return self

    def tasks(
        self,
        items: Sequence[Union[tuple[str, bool], str]],
        *,
        title: str | None = None,
    ) -> "Report":
        header = f'[TASKS title="{_escape_attr(title)}"]' if title else "[TASKS]"
        lines = [header]
        for item in items:
            if isinstance(item, tuple):
                label, checked = item[0], bool(item[1])
            else:
                label, checked = str(item), False
            mark = "x" if checked else " "
            lines.append(f"- [{mark}] {label}")
        lines.append("[/TASKS]")
        self._blocks.append("\n".join(lines))
        return self

    def callout(
        self,
        body: object,
        *,
        tone: str = "info",
        title: str | None = None,
    ) -> "Report":
        attrs = [f'tone="{_escape_attr(tone)}"']
        if title:
            attrs.append(f'title="{_escape_attr(title)}"')
        header = f"[CALLOUT {' '.join(attrs)}]"
        self._blocks.append(f"{header}\n{str(body).strip()}\n[/CALLOUT]")
        return self

    def card(
        self,
        title: object,
        value: object,
        subtitle: object | None = None,
        *,
        tone: str = "neutral",
    ) -> "Report":
        attrs = [f'title="{_escape_attr(title)}"']
        if tone and tone != "neutral":
            attrs.append(f'tone="{_escape_attr(tone)}"')
        lines = [f"[CARD {' '.join(attrs)}]", str(value)]
        if subtitle is not None:
            lines.append(str(subtitle))
        lines.append("[/CARD]")
        self._blocks.append("\n".join(lines))
        return self

    def cards(
        self,
        items: Sequence[Union[tuple[object, ...], Mapping[str, object]]],
        *,
        gap: int = 16,
    ) -> "Report":
        if not items:
            return self
        parts = [f'[COLUMNS gap="{int(gap)}"]']
        for item in items:
            if isinstance(item, Mapping):
                title = str(item.get("title", "Metric"))
                value = item.get("value", "")
                subtitle = item.get("subtitle")
                tone = str(item.get("tone", "neutral"))
            else:
                title = str(item[0]) if len(item) > 0 else "Metric"
                value = item[1] if len(item) > 1 else ""
                subtitle = str(item[2]) if len(item) > 2 and item[2] is not None else None
                tone = "neutral"
            attrs = [f'title="{_escape_attr(title)}"']
            if tone and tone != "neutral":
                attrs.append(f'tone="{_escape_attr(tone)}"')
            card_lines = [f"[CARD {' '.join(attrs)}]", str(value)]
            if subtitle is not None:
                card_lines.append(str(subtitle))
            card_lines.append("[/CARD]")
            parts.append("\n".join(card_lines))
        parts.append("[/COLUMNS]")
        self._blocks.append("\n\n".join(parts))
        return self

    def table(
        self,
        headers: Sequence[object],
        rows: Sequence[Sequence[object]],
        *,
        title: str | None = None,
    ) -> "Report":
        if title:
            self.h3(title)
        hdr = "| " + " | ".join(_escape_cell(h) for h in headers) + " |"
        sep = "| " + " | ".join("---" for _ in headers) + " |"
        body = [
            "| " + " | ".join(_escape_cell(c) for c in row) + " |"
            for row in rows
        ]
        self._blocks.append("\n".join([hdr, sep, *body]))
        return self

    # -- AI & Data Graphics ---------------------------------------------------

    def pipeline(self, stages: Sequence[object], *, title: str = "Pipeline") -> "Report":
        flow = " -> ".join(str(s).strip() for s in stages if str(s).strip())
        self._blocks.append(
            f'[PIPELINE title="{_escape_attr(title)}"]\n{flow}\n[/PIPELINE]'
        )
        return self

    def progress(self, label: object, value: Number, *, max_value: Number = 100) -> "Report":
        self._blocks.append(
            f'[PROGRESS label="{_escape_attr(label)}" value="{_format_num(value)}" max="{_format_num(max_value)}" /]'
        )
        return self

    def chart(
        self,
        title: object,
        data: Union[Mapping[str, object], Sequence[tuple[object, ...]]],
        *,
        chart_type: str = "bar",
        series: Sequence[str] | None = None,
    ) -> "Report":
        valid_types = ("bar", "column", "pie", "line", "curved", "comparison")
        if chart_type not in valid_types:
            raise ValueError(
                f"chart_type inválido: {chart_type!r} (use um de {', '.join(valid_types)})"
            )
        lines = [f'[CHART title="{_escape_attr(title)}" type="{chart_type}"]']
        if series:
            lines.append("SERIES: " + " | ".join(_escape_cell(s) for s in series))

        rows: Iterable[tuple[object, ...]]
        if isinstance(data, Mapping):
            rows = [(k, v) for k, v in data.items()]
        else:
            rows = data

        for row in rows:
            label = _escape_cell(row[0])
            raw_vals = row[1] if len(row) == 2 and isinstance(row[1], (list, tuple)) else row[1:]
            vals = [_format_num(v) for v in raw_vals]
            lines.append(f"{label} | " + " | ".join(vals))

        lines.append("[/CHART]")
        self._blocks.append("\n".join(lines))
        return self

    def bar_chart(self, title: object, data: Union[Mapping[str, object], Sequence[tuple[object, ...]]]) -> "Report":
        return self.chart(title, data, chart_type="bar")

    def column_chart(self, title: object, data: Union[Mapping[str, object], Sequence[tuple[object, ...]]]) -> "Report":
        return self.chart(title, data, chart_type="column")

    def pie_chart(self, title: object, data: Union[Mapping[str, object], Sequence[tuple[object, ...]]]) -> "Report":
        return self.chart(title, data, chart_type="pie")

    def line_chart(
        self,
        title: object,
        data: Sequence[tuple[object, ...]],
        *,
        series: Sequence[str] | None = None,
    ) -> "Report":
        return self.chart(title, data, chart_type="line", series=series)

    def curved_chart(
        self,
        title: object,
        data: Sequence[tuple[object, ...]],
        *,
        series: Sequence[str] | None = None,
    ) -> "Report":
        return self.chart(title, data, chart_type="curved", series=series)

    def comparison_chart(
        self,
        title: object,
        data: Sequence[tuple[object, ...]],
        *,
        series: Sequence[str] | None = None,
    ) -> "Report":
        return self.chart(title, data, chart_type="comparison", series=series)

    # -- Output ---------------------------------------------------------------

    def render(self) -> str:
        return "\n\n".join(b for b in self._blocks if b is not None).rstrip() + "\n"

    def __str__(self) -> str:
        return self.render()

    def save(self, path: Union[str, Path]) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.render(), encoding="utf-8")
        return target
