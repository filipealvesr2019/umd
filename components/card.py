"""Componentes de agrupamento e informação: CARD, CALLOUT, COLUMNS."""
from __future__ import annotations

from ..core.ast import Diagnostic, Node
from .base import Component, PropSpec
from .registry import register

TONES = ("neutral", "success", "warning", "danger", "info")


@register
class Card(Component):
    name = "CARD"
    props = {
        "title": PropSpec("str"),
        "tone": PropSpec("enum", "neutral", choices=TONES),
        "padding": PropSpec("int", 16),
        "width": PropSpec("int"),
    }


@register
class Callout(Component):
    name = "CALLOUT"
    props = {
        "tone": PropSpec("enum", "info", choices=TONES),
        "title": PropSpec("str"),
        "icon": PropSpec("str"),
    }

    def validate(self, node: Node) -> list[Diagnostic]:
        diagnostics = super().validate(node)
        if not node.children:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "W_EMPTY_CALLOUT",
                    "[CALLOUT] está vazio",
                    node.line,
                    node.column,
                    node.start,
                    node.end,
                    node.id,
                )
            )
        return diagnostics


@register
class Columns(Component):
    name = "COLUMNS"
    props = {
        "gap": PropSpec("int", 16),
        "equal": PropSpec("bool", True),
        "wrap": PropSpec("bool", False),
    }
