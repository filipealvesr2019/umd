"""Componente PROGRESS: barra de progresso visual e interativa."""
from __future__ import annotations

from .base import Component, PropSpec
from .registry import register


@register
class Progress(Component):
    name = "PROGRESS"
    props = {
        "value": PropSpec("int", 0),
        "label": PropSpec("str", "Progresso"),
        "max": PropSpec("int", 100),
    }
