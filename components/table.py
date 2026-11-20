"""Componente TABLE: tabela editável com corpo bruto.

O corpo da tabela não é Markdown: cada linha é uma linha de tabela e as
células são separadas por ``|``. Cada célula guarda o span exato do texto no
arquivo, o que permite editar uma célula sem tocar no resto do documento.
"""
from __future__ import annotations

import re
from typing import Iterator

from ..core.ast import Diagnostic, IdAllocator, Node
from .base import Component, PropSpec
from .registry import register

ALIGN_CELL_RE = re.compile(r"^:?-{3,}:?$")


@register
class Table(Component):
    name = "TABLE"
    raw_body = True
    props = {
        "title": PropSpec("str"),
        "dense": PropSpec("bool", False),
        "striped": PropSpec("bool", True),
    }

    def validate(self, node: Node) -> list[Diagnostic]:
        diagnostics = super().validate(node)
        rows = [child for child in node.children if child.type == "table_row"]
        if not rows:
            diagnostics.append(
                Diagnostic(
                    "error",
                    "E_EMPTY_TABLE",
                    "[TABLE] precisa de ao menos uma linha (a primeira é o cabeçalho)",
                    node.line,
                    node.column,
                    node.start,
                    node.end,
                    node.id,
                )
            )
            return diagnostics
        header_cols = len(rows[0].children)
        for row in rows[1:]:
            if row.props.get("align"):
                continue
            if len(row.children) != header_cols:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_COLUMN_COUNT",
                        f"[TABLE] linha {row.line} tem {len(row.children)} células; "
                        f"o cabeçalho tem {header_cols}",
                        row.line,
                        row.column,
                        row.start,
                        row.end,
                        node.id,
                    )
                )
        return diagnostics


def split_pipes(raw: str) -> list[tuple[int, int]]:
    """Divide uma linha de tabela em segmentos ``(início, fim)``."""
    segments: list[tuple[int, int]] = []
    cursor = 0
    index = 0
    while index < len(raw):
        char = raw[index]
        if char == "\\":
            index += 2
            continue
        if char == "|":
            segments.append((cursor, index))
            cursor = index + 1
        index += 1
    segments.append((cursor, len(raw)))

    if raw.strip().startswith("|") and segments and not raw[: segments[0][1]].strip():
        segments = segments[1:]
    if raw.strip().endswith("|") and segments and not raw[segments[-1][0] :].strip():
        segments = segments[:-1]
    return segments


def build_row(token, alloc: IdAllocator, logical_row: int) -> Node:
    """Constrói um nó ``table_row`` a partir de um token ``MD_LINE``."""
    raw = token.raw
    segments = split_pipes(raw)
    texts = [raw[start:end].strip() for start, end in segments]
    is_align = bool(texts) and all(ALIGN_CELL_RE.match(text) for text in texts) and logical_row == 1

    row = Node(
        "table_row",
        id=alloc.next("table_row"),
        text=raw,
        start=token.start,
        end=token.end,
        line=token.line,
        column=token.column,
        props={
            "row": None if is_align else logical_row,
            "header": logical_row == 0,
            "align": is_align,
        },
        meta={"outer_pipes": raw.strip().startswith("|"), "raw": raw},
    )

    for column, (start, end) in enumerate(segments):
        segment = raw[start:end]
        leading = len(segment) - len(segment.lstrip())
        trailing = len(segment) - len(segment.rstrip())
        cell_start = token.start + start + leading
        cell_end = token.start + end - trailing if end - trailing >= start + leading else cell_start
        cell = Node(
            "table_cell",
            id=alloc.next("cell"),
            text=segment.strip(),
            start=cell_start,
            end=cell_end,
            line=token.line,
            column=token.column + start + leading,
            props={
                "row": None if is_align else logical_row,
                "col": column,
                "header": logical_row == 0,
                "align": "align" if is_align else None,
            },
            meta={"segment_start": token.start + start, "segment_end": token.start + end},
        )
        row.add(cell)
    return row


def rows(node: Node) -> list[Node]:
    return [child for child in node.children if child.type == "table_row"]


def data_rows(node: Node) -> list[Node]:
    return [row for row in rows(node) if not row.props.get("align")]


def header_row(node: Node) -> Node | None:
    data = data_rows(node)
    return data[0] if data else None


def unescape_cell(text: str) -> str:
    return text.replace("\\|", "|")


def alignment(node: Node) -> list[str]:
    """Alinhamento por coluna, lido da linha de alinhamento (se existir)."""
    for row in rows(node):
        if not row.props.get("align"):
            continue
        aligns: list[str] = []
        for cell in row.children:
            raw = cell.text
            left = raw.startswith(":")
            right = raw.endswith(":")
            aligns.append("center" if left and right else "right" if right else "left")
        return aligns
    return []


def grid(node: Node) -> list[list[str]]:
    """Valores textuais da tabela (sem a linha de alinhamento)."""
    return [[unescape_cell(cell.text) for cell in row.children] for row in data_rows(node)]


def row_style(node: Node) -> dict[str, bool]:
    header = header_row(node)
    outer = bool(header and header.meta.get("outer_pipes"))
    return {"outer_pipes": outer}


def format_row(values: list[str], style: dict[str, bool]) -> str:
    cells = [str(value).replace("|", "\\|") for value in values]
    body = " | ".join(cells)
    if style.get("outer_pipes", True):
        return f"| {body} |"
    return body


def iter_cells(node: Node) -> Iterator[Node]:
    for row in data_rows(node):
        for cell in row.children:
            yield cell
