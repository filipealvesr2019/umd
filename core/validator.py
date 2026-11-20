"""Validação estrutural da AST."""
from __future__ import annotations

from ..components import registry
from .ast import Diagnostic, Node


def validate(root: Node) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    _walk(root, diagnostics)
    diagnostics.sort(key=lambda d: (d.line, d.column, d.code))
    return diagnostics


def _walk(node: Node, diagnostics: list[Diagnostic]) -> None:
    if node.type == "component":
        component = registry.get(node.name)
        if component is None:
            diagnostics.append(
                Diagnostic(
                    "error",
                    "E_UNKNOWN_COMPONENT",
                    f"componente [{node.name}] não registrado",
                    node.line,
                    node.column,
                    node.start,
                    node.end,
                    node.id,
                )
            )
        else:
            diagnostics.extend(component().validate(node))

    for child in node.children:
        _walk(child, diagnostics)


def errors(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    return [d for d in diagnostics if d.level == "error"]


def warnings(diagnostics: list[Diagnostic]) -> list[Diagnostic]:
    return [d for d in diagnostics if d.level == "warning"]


def format_diagnostics(path: str, diagnostics: list[Diagnostic]) -> str:
    lines = [str(d).replace("documento:", f"{path}:") for d in diagnostics]
    return "\n".join(lines)
