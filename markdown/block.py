"""Nós de bloco Markdown: título, parágrafo, lista, citação, código, hr."""
from __future__ import annotations

import re

from ..core.ast import Diagnostic, IdAllocator, Node
from .inline import parse_inline

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*)$")
FENCE_RE = re.compile(r"^(```+|~~~+)(.*)$")
LIST_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])[ \t]+(.*)$")
QUOTE_RE = re.compile(r"^\s*>[ ]?(.*)$")
HR_RE = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")


def block_start(raw: str) -> str | None:
    """Classifica uma linha como início de bloco, ou ``None`` se for texto."""
    stripped = raw.strip()
    if HR_RE.match(stripped):
        return "hr"
    if HEADING_RE.match(raw):
        return "heading"
    if FENCE_RE.match(stripped):
        return "code_block"
    if QUOTE_RE.match(raw):
        return "quote"
    if LIST_RE.match(raw):
        return "list"
    return None


def build_block(
    tokens, index: int, alloc: IdAllocator, diagnostics: list[Diagnostic]
) -> tuple[list[Node], int]:
    """Constrói um bloco Markdown a partir de ``tokens[index]``.

    Retorna os nós criados e o próximo índice de token.
    """
    kind = block_start(tokens[index].raw)
    if kind == "heading":
        return _heading(tokens[index], alloc), index + 1
    if kind == "hr":
        token = tokens[index]
        node = Node(
            "hr",
            id=alloc.next("hr"),
            text=token.raw,
            start=token.start,
            end=token.end,
            line=token.line,
            column=token.column,
        )
        return [node], index + 1
    if kind == "code_block":
        return _code_block(tokens, index, alloc, diagnostics)
    if kind == "list":
        return _list(tokens, index, alloc)
    if kind == "quote":
        return _quote(tokens, index, alloc)
    return _paragraph(tokens, index, alloc)


def _heading(token, alloc: IdAllocator) -> list[Node]:
    match = HEADING_RE.match(token.raw)
    level = len(match.group(1))
    content = match.group(2)
    offset = token.start + match.start(2)
    node = Node(
        "heading",
        id=alloc.next("heading"),
        text=content,
        props={"level": level},
        start=token.start,
        end=token.end,
        line=token.line,
        column=token.column,
        meta={"text_start": offset, "text_end": offset + len(content)},
    )
    for child in parse_inline(content, offset, alloc, token.line, token.column + match.start(2)):
        node.add(child)
    return [node]


def _code_block(tokens, index: int, alloc: IdAllocator, diagnostics: list[Diagnostic]) -> tuple[list[Node], int]:
    opener = tokens[index]
    fence = FENCE_RE.match(opener.raw.strip()).group(1)
    marker = fence[0]
    body: list[str] = []
    cursor = index + 1
    closed = False
    while cursor < len(tokens) and tokens[cursor].type.value != "EOF":
        token = tokens[cursor]
        if token.type.value == "MD_LINE" and token.raw.strip().startswith(marker * 3):
            if set(token.raw.strip()) <= {marker} or token.raw.strip().startswith(fence):
                closed = True
                break
        body.append(token.raw)
        cursor += 1
    if not closed:
        diagnostics.append(
            Diagnostic(
                "error",
                "E_UNCLOSED_FENCE",
                f"bloco de código aberto na linha {opener.line} não foi fechado",
                opener.line,
                opener.column,
                opener.start,
                opener.end,
            )
        )
    end_token = tokens[cursor] if closed else tokens[max(cursor - 1, index)]
    node = Node(
        "code_block",
        id=alloc.next("code_block"),
        text="\n".join(body),
        props={"lang": opener.raw.strip()[len(fence) :].strip()},
        start=opener.start,
        end=end_token.end,
        line=opener.line,
        column=opener.column,
    )
    return [node], cursor + 1 if closed else cursor


def _list(tokens, index: int, alloc: IdAllocator) -> tuple[list[Node], int]:
    items: list[Node] = []
    cursor = index
    first = tokens[index]
    while cursor < len(tokens) and tokens[cursor].type.value == "MD_LINE":
        token = tokens[cursor]
        match = LIST_RE.match(token.raw)
        if not match:
            break
        content = match.group(2)
        offset = token.start + match.start(2)
        item = Node(
            "list_item",
            id=alloc.next("list_item"),
            text=content,
            start=token.start,
            end=token.end,
            line=token.line,
            column=token.column,
            meta={"text_start": offset, "text_end": offset + len(content)},
        )
        for child in parse_inline(content, offset, alloc, token.line, token.column + match.start(2)):
            item.add(child)
        items.append(item)
        cursor += 1
    node = Node(
        "list",
        id=alloc.next("list"),
        start=first.start,
        end=tokens[cursor - 1].end,
        line=first.line,
        column=first.column,
        meta={"ordered": bool(first.raw.strip()[:1].isdigit())},
    )
    for item in items:
        node.add(item)
    return [node], cursor


def _quote(tokens, index: int, alloc: IdAllocator) -> tuple[list[Node], int]:
    lines: list[str] = []
    cursor = index
    first = tokens[index]
    last = first
    while cursor < len(tokens) and tokens[cursor].type.value == "MD_LINE":
        token = tokens[cursor]
        match = QUOTE_RE.match(token.raw)
        if not match:
            break
        lines.append(match.group(1))
        last = token
        cursor += 1
    content = "\n".join(lines)
    node = Node(
        "quote",
        id=alloc.next("quote"),
        text=content,
        start=first.start,
        end=last.end,
        line=first.line,
        column=first.column,
        meta={"text_start": first.start, "text_end": last.end},
    )
    for child in parse_inline(content, first.start, alloc, first.line, first.column):
        node.add(child)
    return [node], cursor


def _paragraph(tokens, index: int, alloc: IdAllocator) -> tuple[list[Node], int]:
    cursor = index
    lines: list[str] = []
    first = tokens[index]
    last = first
    while cursor < len(tokens) and tokens[cursor].type.value == "MD_LINE":
        token = tokens[cursor]
        if block_start(token.raw) is not None:
            break
        lines.append(token.raw)
        last = token
        cursor += 1
    node = Node(
        "paragraph",
        id=alloc.next("paragraph"),
        text="\n".join(lines),
        start=first.start,
        end=last.end,
        line=first.line,
        column=first.column,
        meta={"text_start": first.start, "text_end": last.end},
    )
    for offset, line_text in enumerate(lines):
        token = tokens[index + offset]
        for child in parse_inline(line_text, token.start, alloc, token.line, token.column):
            node.add(child)
    return [node], cursor
