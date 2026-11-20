"""Contratos dos componentes UMD (independentes de qualquer renderizador)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.ast import Diagnostic, Node


@dataclass(frozen=True)
class PropSpec:
    kind: str = "str"  # str | int | number | bool | enum
    default: Any = None
    required: bool = False
    choices: tuple[str, ...] = ()


class Component:
    """Um componente declarativo.

    Nenhum método aqui sabe desenhar nada: o componente descreve o que aceita
    e valida a própria árvore. O desenho é responsabilidade do renderizador.
    """

    name: str = ""
    props: dict[str, PropSpec] = {}
    #: True quando o corpo do componente não é Markdown (ex: tabela).
    raw_body: bool = False
    #: True quando as propriedades podem ser alteradas por edição visual.
    editable_props: bool = True

    def validate(self, node: Node) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        attrs = node.meta.get("attrs", {})
        for key, spec in self.props.items():
            if spec.required and key not in attrs:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_REQUIRED_PROP",
                        f"[{self.name}] exige o atributo '{key}'",
                        node.line,
                        node.column,
                        node.start,
                        node.end,
                        node.id,
                    )
                )
        for key, attr in attrs.items():
            spec = self.props.get(key)
            if spec is None:
                diagnostics.append(
                    Diagnostic(
                        "warning",
                        "W_UNKNOWN_PROP",
                        f"[{self.name}] não conhece o atributo '{key}'",
                        node.line,
                        node.column,
                        attr.start,
                        attr.end,
                        node.id,
                    )
                )
                continue
            problem = _check_value(spec, attr.value)
            if problem:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_PROP_VALUE",
                        f"[{self.name}] atributo '{key}': {problem}",
                        node.line,
                        node.column,
                        attr.start,
                        attr.end,
                        node.id,
                    )
                )
        return diagnostics


def _check_value(spec: PropSpec, value: str | None) -> str | None:
    if value is None:
        if spec.kind in ("int", "number") or spec.required:
            return "valor ausente"
        return None
    if spec.kind == "int":
        try:
            int(value)
        except ValueError:
            return f"esperado inteiro, recebido '{value}'"
    elif spec.kind == "number":
        try:
            float(value)
        except ValueError:
            return f"esperado número, recebido '{value}'"
    elif spec.kind == "bool":
        if value.lower() not in ("true", "false", "1", "0", "sim", "nao", "não"):
            return f"esperado booleano, recebido '{value}'"
    elif spec.kind == "enum" and value not in spec.choices:
        return f"esperado um de {list(spec.choices)}, recebido '{value}'"
    return None


def props_of(node: Node) -> dict[str, Any]:
    """Valores efetivos: atributos do documento sobre os defaults do schema."""
    from .registry import get

    component = get(node.name)
    values: dict[str, Any] = {}
    if component is not None:
        for key, spec in component.props.items():
            values[key] = spec.default
    for key, attr in node.meta.get("attrs", {}).items():
        values[key] = attr.value if attr.value is not None else True
    return values
