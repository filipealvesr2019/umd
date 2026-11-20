"""Componente PIPELINE: diagramas de fluxo de arquitetura e pipelines de IA."""
from __future__ import annotations

from .base import Component, PropSpec
from .registry import register


@register
class Pipeline(Component):
    name = "PIPELINE"
    raw_body = True
    props = {
        "title": PropSpec("str", "AI Pipeline"),
    }
