"""Lexer do UMD: texto -> tokens com posições exatas.

O lexer é independente de componentes: ele só reconhece tags, comentários,
linhas em branco e linhas de conteúdo. Quem decide o que é tabela, card ou
parágrafo é o parser, consultando o registry de componentes.
"""
from __future__ import annotations

import re

from .tokens import Attribute, Token, TokenType

NAME = r"[A-Za-z\u00C0-\u00FF][A-Za-z0-9_\u00C0-\u00FF-]*"

_OPEN_RE = re.compile(rf"\[\s*(?P<name>{NAME})(?P<attrs>[^\]]*)\]")
_CLOSE_RE = re.compile(rf"\[\s*/\s*(?P<name>{NAME})\s*\]")
_COLON_OPEN_RE = re.compile(rf"::\s*(?P<name>{NAME})(?:\s+(?P<attrs>.*))?")
_COLON_CLOSE_RE = re.compile(r"::")
_ATTR_RE = re.compile(
    r"""(?P<name>[A-Za-z_][A-Za-z0-9_-]*)"""
    r"""(?:\s*=\s*(?P<value>"[^"]*"|'[^']*'|[^\s"']+))?"""
)


def _parse_attrs(attrs_text: str, base: int) -> list[Attribute]:
    attrs: list[Attribute] = []
    for match in _ATTR_RE.finditer(attrs_text):
        start = base + match.start()
        end = base + match.end()
        raw_value = match.group("value")
        if raw_value is None:
            attrs.append(Attribute(match.group("name"), None, start, end))
            continue
        quoted = raw_value[:1] in {'"', "'"}
        value = raw_value[1:-1] if quoted else raw_value
        value_start = base + match.start("value") + (1 if quoted else 0)
        value_end = base + match.end("value") - (1 if quoted else 0)
        attrs.append(
            Attribute(
                match.group("name"),
                value,
                start,
                end,
                value_start=value_start,
                value_end=value_end,
                quoted=quoted,
            )
        )
    return attrs


def lex(text: str) -> list[Token]:
    """Tokeniza ``text`` (texto já normalizado para ``\\n``)."""
    tokens: list[Token] = []
    lines = text.split("\n")
    offset = 0
    index = 0
    total = len(lines)

    while index < total:
        content = lines[index]
        start = offset
        offset += len(content) + 1
        line_no = index + 1
        stripped = content.lstrip()
        column = len(content) - len(stripped) + 1

        if not stripped:
            tokens.append(Token(TokenType.BLANK, content, start, start + len(content), line_no, column))
            index += 1
            continue

        if stripped.startswith("<!--"):
            end_offset, last_index = _comment_end(lines, index, start)
            raw = text[start:end_offset]
            tokens.append(Token(TokenType.COMMENT, raw, start, end_offset, line_no, column))
            offset = end_offset + 1
            index = last_index + 1
            continue

        tag_start = start + (len(content) - len(stripped))

        close = _CLOSE_RE.fullmatch(stripped)
        if close:
            tokens.append(
                Token(
                    TokenType.COMPONENT_CLOSE,
                    stripped,
                    tag_start,
                    tag_start + len(stripped),
                    line_no,
                    column,
                    name=close.group("name"),
                )
            )
            index += 1
            continue

        opened = _OPEN_RE.fullmatch(stripped)
        if opened and not _is_escaped(content, tag_start - start):
            attrs_text = opened.group("attrs")
            self_closing = attrs_text.rstrip().endswith("/")
            if self_closing:
                attrs_text = attrs_text.rstrip()[:-1]
                attrs_text = attrs_text.rstrip()
            attrs_base = tag_start + opened.start("attrs")
            token_type = TokenType.COMPONENT_SELF if self_closing else TokenType.COMPONENT_OPEN
            tokens.append(
                Token(
                    token_type,
                    stripped,
                    tag_start,
                    tag_start + len(stripped),
                    line_no,
                    column,
                    name=opened.group("name"),
                    attrs=_parse_attrs(attrs_text, attrs_base),
                )
            )
            index += 1
            continue

        tokens.append(Token(TokenType.MD_LINE, content, start, start + len(content), line_no, column))
        index += 1

    tokens.append(Token(TokenType.EOF, "", len(text), len(text), max(total, 1), 1))
    return tokens


def _is_escaped(content: str, position: int) -> bool:
    """True se o caractere em ``position`` está precedido por ``\\``."""
    backslashes = 0
    cursor = position - 1
    while cursor >= 0 and content[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def _comment_end(lines: list[str], index: int, start_offset: int) -> tuple[int, int]:
    """Encontra o fim de um comentário ``<!-- ... -->`` (pode ser multilinha)."""
    offset = start_offset
    cursor = index
    while cursor < len(lines):
        line = lines[cursor]
        found = line.find("-->")
        if found != -1:
            return offset + found + 3, cursor
        offset += len(line) + 1
        cursor += 1
    return start_offset + len(lines[index]), index
