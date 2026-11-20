"""Source mapping: liga cada nó da AST ao trecho exato do arquivo."""
from __future__ import annotations

from typing import Any

from ..core.ast import Diagnostic, Node


class SourceMap:
    def __init__(self, root: Node) -> None:
        self.root = root
        self.nodes: dict[str, Node] = {}
        self.attrs: dict[tuple[str, str], Any] = {}
        self.cells: dict[tuple[str, int, int], Node] = {}
        self._index(root)

    @classmethod
    def from_root(cls, root: Node) -> "SourceMap":
        return cls(root)

    def _index(self, node: Node) -> None:
        self.nodes[node.id] = node
        for key, attr in node.meta.get("attrs", {}).items():
            self.attrs[(node.id, key)] = attr
        if node.type == "table_cell":
            row = node.props.get("row")
            if row is not None:
                table = _table_of(node)
                if table is not None:
                    self.cells[(table.id, row, node.props["col"])] = node
        for child in node.children:
            self._index(child)

    # -- consultas --------------------------------------------------
    def span(self, node_id: str) -> tuple[int, int] | None:
        node = self.nodes.get(node_id)
        return (node.start, node.end) if node else None

    def cell(self, table_id: str, row: int, col: int) -> Node | None:
        return self.cells.get((table_id, row, col))

    def cell_span(self, table_id: str, row: int, col: int) -> tuple[int, int] | None:
        cell = self.cell(table_id, row, col)
        return (cell.start, cell.end) if cell else None

    def attr_span(self, node_id: str, key: str) -> tuple[int, int] | None:
        attr = self.attrs.get((node_id, key))
        if attr is None:
            return None
        return (attr.start, attr.end)

    def node_at(self, offset: int) -> Node | None:
        """Nó mais específico que contém ``offset``."""
        best: Node | None = None
        for node in self.nodes.values():
            if node.start <= offset < node.end:
                if best is None or (node.end - node.start) < (best.end - best.start):
                    best = node
        return best

    # -- integridade ------------------------------------------------
    def check(self, text: str) -> list[Diagnostic]:
        """Verifica limites e aninhamento dos spans."""
        diagnostics: list[Diagnostic] = []
        for node in self.nodes.values():
            if node.start > node.end or node.end > len(text):
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_SPAN_RANGE",
                        f"span inválido [{node.start}, {node.end}) em {node.id}",
                        node.line,
                        node.column,
                        node.start,
                        node.end,
                        node.id,
                    )
                )
            if node.parent is not None and not (
                node.parent.start <= node.start and node.end <= node.parent.end
            ):
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_SPAN_PARENT",
                        f"{node.id} fora do span do pai {node.parent.id}",
                        node.line,
                        node.column,
                        node.start,
                        node.end,
                        node.id,
                    )
                )
        for parent in self.nodes.values():
            children = sorted(parent.children, key=lambda c: c.start)
            for previous, current in zip(children, children[1:]):
                if current.start < previous.end:
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "E_SPAN_OVERLAP",
                            f"{current.id} sobrepõe {previous.id}",
                            current.line,
                            current.column,
                            current.start,
                            current.end,
                            current.id,
                        )
                    )
        return diagnostics


def _table_of(node: Node) -> Node | None:
    cursor = node.parent
    while cursor is not None:
        if cursor.is_component and cursor.name == "TABLE":
            return cursor
        cursor = cursor.parent
    return None
