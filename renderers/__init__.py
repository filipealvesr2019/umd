"""Renderizadores do UMD.

Cada renderizador consome a AST e produz uma saída específica. O documento
original nunca é tocado: renderizar é uma leitura.
"""
from .html import render_document as render_html

__all__ = ["render_html"]
