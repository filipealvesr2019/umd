"""Árvore de componentes (AST) e diagnósticos do UMD."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator


@dataclass
class Diagnostic:
    level: str
    code: str
    message: str
    line: int = 0
    column: int = 0
    start: int = 0
    end: int = 0
    node_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "span": [self.start, self.end],
            "node": self.node_id,
        }

    def __str__(self) -> str:
        loc = f"linha {self.line}, coluna {self.column}" if self.line else "documento"
        return f"{self.level}: {loc}: [{self.code}] {self.message}"


@dataclass
class Node:
    """Um nó da AST.

    ``start`` e ``end`` são deslocamentos no texto normalizado. Eles são o
    vínculo entre a representação visual e o arquivo original.
    """

    type: str
    id: str = ""
    text: str = ""
    props: dict[str, Any] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    start: int = 0
    end: int = 0
    line: int = 1
    column: int = 1
    parent: "Node | None" = field(default=None, repr=False)
    meta: dict[str, Any] = field(default_factory=dict)

    # -- construção -------------------------------------------------
    def add(self, child: "Node") -> "Node":
        child.parent = self
        self.children.append(child)
        return child

    # -- consulta ---------------------------------------------------
    def walk(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def find(self, node_id: str) -> "Node | None":
        for node in self.walk():
            if node.id == node_id:
                return node
        return None

    @property
    def name(self) -> str:
        if self.type == "component":
            return str(self.props.get("name", "")).upper()
        return self.type

    @property
    def is_component(self) -> bool:
        return self.type == "component"

    @property
    def length(self) -> int:
        return max(0, self.end - self.start)

    def to_dict(self, with_span: bool = True, with_children: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {"id": self.id, "type": self.type}
        if self.type == "component":
            data["name"] = self.name
        if self.text:
            data["text"] = self.text
        attrs = {
            key: (attr.value if attr.value is not None else True)
            for key, attr in self.meta.get("attrs", {}).items()
        }
        props = dict(self.props)
        props.pop("name", None)
        props.pop("attrs", None)
        if props:
            data["props"] = props
        if attrs:
            data["attrs"] = attrs
        if with_span:
            data["span"] = [self.start, self.end]
            data["line"] = self.line
            data["column"] = self.column
        if with_children and self.children:
            data["children"] = [c.to_dict(with_span, with_children) for c in self.children]
        return data


class IdAllocator:
    """Ids estáveis e legíveis: ``table#1``, ``paragraph#2``, ``cell#7``."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def next(self, prefix: str) -> str:
        self._counts[prefix] = self._counts.get(prefix, 0) + 1
        return f"{prefix}#{self._counts[prefix]}"

    def to_dict(self) -> dict[str, int]:
        return dict(self._counts)
