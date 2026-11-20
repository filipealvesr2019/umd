"""Elementos inline do Markdown: forte, ênfase, código, link, riscado."""
from __future__ import annotations

import re

from ..core.ast import IdAllocator, Node

INLINE_RE = re.compile(
    r"(?P<code>`[^`\n]+`)"
    r"|(?P<strong>\*\*[^*\n]+\*\*|__[^_\n]+__)"
    r"|(?P<strike>~~[^~\n]+~~)"
    r"|(?P<link>\[[^\]\n]+\]\([^)\n]+\))"
    r"|(?P<em>\*[^*\n]+\*|_[^_\n]+_)"
)

_LINK_RE = re.compile(r"\[(?P<label>[^\]\n]+)\]\((?P<url>[^)\n]+)\)")

_STRIP = {
    "code": (1, 1),
    "strong": (2, 2),
    "strike": (2, 2),
    "em": (1, 1),
}


def parse_inline(text: str, base: int, alloc: IdAllocator, line: int, column: int) -> list[Node]:
    """Converte uma linha de Markdown inline em nós com spans absolutos."""
    nodes: list[Node] = []
    cursor = 0

    for match in INLINE_RE.finditer(text):
        begin = match.start()
        if begin < cursor:
            continue  # já consumido por um match anterior (sobreposição)
        if begin > 0 and text[begin - 1] == "\\":
            continue  # escapado

        if begin > cursor:
            nodes.append(_text_node(text[cursor:begin], base + cursor, alloc, line, column + cursor))

        kind = match.lastgroup
        raw = match.group(0)
        if kind == "link":
            parts = _LINK_RE.match(raw)
            node = Node(
                "link",
                id=alloc.next("link"),
                text=parts.group("label"),
                props={"url": parts.group("url")},
                start=base + begin,
                end=base + match.end(),
                line=line,
                column=column + begin,
            )
            nodes.append(node)
        else:
            strip_left, strip_right = _STRIP[kind]
            node = Node(
                kind,
                id=alloc.next(kind),
                text=raw[strip_left : len(raw) - strip_right],
                start=base + begin,
                end=base + match.end(),
                line=line,
                column=column + begin,
            )
            nodes.append(node)
        cursor = match.end()

    if cursor < len(text):
        nodes.append(_text_node(text[cursor:], base + cursor, alloc, line, column + cursor))
    if not nodes:
        nodes.append(_text_node("", base, alloc, line, column))
    return nodes


def _text_node(text: str, start: int, alloc: IdAllocator, line: int, column: int) -> Node:
    return Node(
        "text",
        id=alloc.next("text"),
        text=text,
        start=start,
        end=start + len(text),
        line=line,
        column=column,
    )
