"""Tokens do lexer UMD."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TokenType(str, Enum):
    MD_LINE = "MD_LINE"
    BLANK = "BLANK"
    COMPONENT_OPEN = "COMPONENT_OPEN"
    COMPONENT_CLOSE = "COMPONENT_CLOSE"
    COMPONENT_SELF = "COMPONENT_SELF"
    COMMENT = "COMMENT"
    EOF = "EOF"


@dataclass
class Attribute:
    """Um atributo de componente, com a posição exata de cada parte."""

    name: str
    value: str | None
    start: int
    end: int
    value_start: int | None = None
    value_end: int | None = None
    quoted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "quoted": self.quoted,
            "span": [self.start, self.end],
            "value_span": (
                [self.value_start, self.value_end]
                if self.value_start is not None
                else None
            ),
        }


@dataclass
class Token:
    type: TokenType
    raw: str
    start: int
    end: int
    line: int
    column: int
    name: str | None = None
    attrs: list[Attribute] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "type": self.type.value,
            "raw": self.raw,
            "start": self.start,
            "end": self.end,
            "line": self.line,
            "column": self.column,
        }
        if self.name is not None:
            data["name"] = self.name
        if self.attrs:
            data["attrs"] = [a.to_dict() for a in self.attrs]
        return data
