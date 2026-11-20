"""Componente CHART: gráficos visuais interativos (benchmark, métricas de IA)."""
from __future__ import annotations

from .base import Component, PropSpec
from .registry import register


@register
class Chart(Component):
    name = "CHART"
    raw_body = True
    props = {
        "title": PropSpec("str", "Benchmark Chart"),
        "type": PropSpec("enum", "bar", choices=("bar", "column", "pie", "line")),
    }
