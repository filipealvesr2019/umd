"""Componente CHART: gráficos visuais interativos (benchmark, métricas de IA)."""
from __future__ import annotations

import re

from ..core.ast import Diagnostic, Node
from .base import Component, PropSpec
from .registry import register

_NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


@register
class Chart(Component):
    name = "CHART"
    raw_body = True
    props = {
        "title": PropSpec("str", "Benchmark Chart"),
        "type": PropSpec(
            "enum",
            "bar",
            choices=("bar", "column", "pie", "line", "curved", "comparison"),
        ),
    }

    def validate(self, node: Node) -> list[Diagnostic]:
        diagnostics = super().validate(node)
        raw_text = node.text or "\n".join(c.text for c in node.children if c.text)
        body_lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        if not body_lines:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "W_EMPTY_CHART",
                    "[CHART] não possui dados",
                    node.line,
                    node.column,
                    node.start,
                    node.end,
                    node.id,
                )
            )
            return diagnostics

        for idx, raw_line in enumerate(body_lines, start=1):
            if raw_line.upper().startswith("SERIES:"):
                continue
            if "|" not in raw_line:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "E_CHART_ROW_FORMAT",
                        f"linha de dados inválida em [CHART]: {raw_line!r} (esperado 'Rótulo | Valor')",
                        node.line + idx,
                        1,
                        node.start,
                        node.end,
                        node.id,
                    )
                )
                continue
            parts = [p.strip() for p in raw_line.split("|")]
            # Allow a column-header first row in multi-series charts (e.g. "Point | Revenue | Margin")
            if (
                idx == 1
                and len(body_lines) > 1
                and len(parts) >= 3
                and all(not _NUM_RE.match(v.rstrip("%").strip()) for v in parts[1:])
            ):
                continue
            for val in parts[1:]:
                cleaned = val.rstrip("%").strip()
                if not cleaned or not _NUM_RE.match(cleaned):
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "E_CHART_NON_NUMERIC",
                            f"valor não numérico em [CHART]: {val!r} na linha {raw_line!r}",
                            node.line + idx,
                            1,
                            node.start,
                            node.end,
                            node.id,
                        )
                    )
        return diagnostics
