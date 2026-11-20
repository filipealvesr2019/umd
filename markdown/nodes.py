"""Área Markdown do UMD."""
from .block import block_start, build_block
from .inline import parse_inline

__all__ = ["block_start", "build_block", "parse_inline"]
