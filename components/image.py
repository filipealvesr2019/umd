"""Componente IMAGE (folha, sem corpo)."""
from __future__ import annotations

from ..core.ast import Diagnostic, Node
from .base import Component, PropSpec
from .registry import register


@register
class Image(Component):
    name = "IMAGE"
    props = {
        "src": PropSpec("str", required=True),
        "alt": PropSpec("str", ""),
        "width": PropSpec("int"),
        "height": PropSpec("int"),
        "caption": PropSpec("str"),
    }

    def validate(self, node: Node) -> list[Diagnostic]:
        diagnostics = super().validate(node)
        if node.children:
            diagnostics.append(
                Diagnostic(
                    "error",
                    "E_NOT_CONTAINER",
                    "[IMAGE] não aceita conteúdo (use a forma auto-fechada)",
                    node.line,
                    node.column,
                    node.start,
                    node.end,
                    node.id,
                )
            )
        return diagnostics
