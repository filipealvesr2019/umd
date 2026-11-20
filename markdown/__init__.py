"""Camada Markdown do UMD."""
from .block import build_block
from .inline import parse_inline

__all__ = ["build_block", "parse_inline"]
