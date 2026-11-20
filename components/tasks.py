"""Componente TASKS: checklist de tarefas estilo Notion."""
from __future__ import annotations

from .base import Component, PropSpec
from .registry import register


@register
class Tasks(Component):
    name = "TASKS"
    props = {
        "title": PropSpec("str"),
    }
