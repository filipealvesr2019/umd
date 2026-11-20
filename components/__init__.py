"""Componentes nativos do UMD."""
from .base import Component, PropSpec, props_of
from .registry import exists, get, instance, is_raw_body, names, register

__all__ = [
    "Component",
    "PropSpec",
    "exists",
    "get",
    "instance",
    "is_raw_body",
    "names",
    "props_of",
    "register",
]
