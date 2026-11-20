"""Parser do UMD: tokens -> AST.

O parser não sabe o que é um card ou uma tabela: ele consulta o registry de
componentes para saber se o nome existe e se o corpo é Markdown ou bruto.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..components import registry
from ..components.table import build_row
from ..markdown.block import build_block
from .ast import Diagnostic, IdAllocator, Node
from .lexer import lex
from .tokens import Token, TokenType


@dataclass
class ParseResult:
    text: str
    root: Node
    tokens: list[Token] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)


def parse(text: str) -> ParseResult:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    tokens = lex(normalized)
    alloc = IdAllocator()
    diagnostics: list[Diagnostic] = []

    root = Node("document", id=alloc.next("document"), start=0, end=len(normalized), line=1, column=1)
    stack: list[Node] = [root]
    index = 0

    while index < len(tokens):
        token = tokens[index]
        if token.type is TokenType.EOF:
            break
        container = stack[-1]

        if token.type is TokenType.BLANK:
            index += 1
            continue

        if token.type is TokenType.COMMENT:
            container.add(
                Node(
                    "comment",
                    id=alloc.next("comment"),
                    text=token.raw,
                    start=token.start,
                    end=token.end,
                    line=token.line,
                    column=token.column,
                )
            )
            index += 1
            continue

        if token.type is TokenType.COMPONENT_OPEN:
            node = _component_node(token, alloc, diagnostics)
            container.add(node)
            stack.append(node)
            index += 1
            continue

        if token.type is TokenType.COMPONENT_SELF:
            node = _component_node(token, alloc, diagnostics)
            node.meta["self_closing"] = True
            container.add(node)
            index += 1
            continue

        if token.type is TokenType.COMPONENT_CLOSE:
            if len(stack) == 1:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_STRAY_CLOSE",
                        f"[/{token.name.upper()}] sem abertura correspondente",
                        token.line,
                        token.column,
                        token.start,
                        token.end,
                    )
                )
            else:
                node = stack.pop()
                if node.name != token.name.upper():
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "E_MISMATCH",
                            f"[/{token.name.upper()}] fecha [{node.name}], aberto na linha {node.line}",
                            token.line,
                            token.column,
                            token.start,
                            token.end,
                            node.id,
                        )
                    )
                node.end = token.end
                node.meta["close_span"] = (token.start, token.end)
                node.meta["close_name_span"] = _name_span(token)
            index += 1
            continue

        # MD_LINE
        if container.is_component and registry.is_raw_body(container.name):
            index = _consume_raw_rows(tokens, index, container, alloc)
        else:
            nodes, index = build_block(tokens, index, alloc, diagnostics)
            for node in nodes:
                container.add(node)

    for node in stack[1:]:
        node.end = len(normalized)
        node.meta["unclosed"] = True
        diagnostics.append(
            Diagnostic(
                "error",
                "E_UNCLOSED",
                f"[{node.name}] aberto na linha {node.line} não foi fechado",
                node.line,
                node.column,
                node.start,
                node.end,
                node.id,
            )
        )

    return ParseResult(normalized, root, tokens, diagnostics)


def _component_node(token: Token, alloc: IdAllocator, diagnostics: list[Diagnostic]) -> Node:
    name = token.name.upper()
    if not registry.exists(name):
        diagnostics.append(
            Diagnostic(
                "error",
                "E_UNKNOWN_COMPONENT",
                f"componente [{name}] desconhecido (conhecidos: {', '.join(registry.names())})",
                token.line,
                token.column,
                token.start,
                token.end,
            )
        )
    node = Node(
        "component",
        id=alloc.next(name.lower()),
        props={"name": name},
        start=token.start,
        end=token.end,
        line=token.line,
        column=token.column,
        meta={
            "attrs": {attr.name: attr for attr in token.attrs},
            "attr_order": [attr.name for attr in token.attrs],
            "tag_start": token.start,
            "tag_end": token.end,
            "attr_insert_at": _attr_insert_position(token),
            "open_name_span": _name_span(token),
            "self_closing": False,
        },
    )
    return node


def _name_span(token: Token) -> tuple[int, int] | None:
    """Posição exata do nome dentro da tag (para renomear componentes)."""
    if not token.name:
        return None
    position = token.raw.upper().find(token.name.upper())
    if position == -1:
        return None
    return (token.start + position, token.start + position + len(token.name))


def _attr_insert_position(token: Token) -> int:
    """Onde inserir um atributo novo: antes de ``]`` (ou de ``/]``)."""
    position = token.end - 1
    while position > token.start and token.raw[position - token.start - 1] in " \t/":
        position -= 1
    return position


def _consume_raw_rows(tokens: list[Token], index: int, table: Node, alloc: IdAllocator) -> int:
    logical = 0
    cursor = index
    while cursor < len(tokens) and tokens[cursor].type in (TokenType.MD_LINE, TokenType.BLANK):
        token = tokens[cursor]
        if token.type is TokenType.MD_LINE:
            row = build_row(token, alloc, logical)
            table.add(row)
            if not row.props.get("align"):
                logical += 1
        cursor += 1
    return cursor
