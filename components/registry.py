"""Registry de componentes.

O parser pergunta ao registry se um nome existe e se seu corpo é bruto.
Novos componentes entram com ``@register``, sem tocar no parser.
"""
from __future__ import annotations

from .base import Component

_REGISTRY: dict[str, type[Component]] = {}
_LOADED = False


def register(cls: type[Component]) -> type[Component]:
    if not cls.name:
        raise ValueError(f"componente {cls.__name__} sem nome")
    _REGISTRY[cls.name.upper()] = cls
    return cls


def _ensure_loaded() -> None:
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    from . import card as _card  # noqa: F401  (registra CARD/CALLOUT/COLUMNS)
    from . import chart as _chart  # noqa: F401  (registra CHART)
    from . import image as _image  # noqa: F401  (registra IMAGE)
    from . import pipeline as _pipeline  # noqa: F401  (registra PIPELINE)
    from . import progress as _progress  # noqa: F401  (registra PROGRESS)
    from . import table as _table  # noqa: F401  (registra TABLE)
    from . import tasks as _tasks  # noqa: F401  (registra TASKS)


def get(name: str) -> type[Component] | None:
    _ensure_loaded()
    return _REGISTRY.get(name.upper())


def exists(name: str) -> bool:
    return get(name) is not None


def is_raw_body(name: str) -> bool:
    component = get(name)
    return bool(component and component.raw_body)


def names() -> list[str]:
    _ensure_loaded()
    return sorted(_REGISTRY)


def instance(name: str) -> Component | None:
    component = get(name)
    return component() if component else None
