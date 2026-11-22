"""UMD — UI Markdown.

Formato de documento em texto puro com componentes visuais. O motor é
independente de qualquer renderizador: ``parse`` produz AST + spans, e o
``Document`` mantém o texto original como fonte da verdade.

Uso rápido::

    from umd import parse_umd, open_document

    resultado = parse_umd("# Olá")
    doc = open_document("relatorio.umd")
    doc.set_cell("table#1", 1, 2, "R$ 13.000")
    doc.save()
"""
from __future__ import annotations

from .builder import Report, bold, inline_code, italic, strike, styled, underline
from .core.parser import ParseResult, parse as parse_umd
from .core.validator import validate
from .document.model import Document
from .document.persistence import open_document, save_document
from .renderers.html import render_document

parse = parse_umd
open = open_document


def view(path: str) -> None:
    """Abre a visualização interativa do documento direto da memória (sem salvar HTML)."""
    import argparse
    from .cli import cmd_view
    cmd_view(argparse.Namespace(file=str(path)))


# Auto-habilita suporte transparente ao editor no ambiente do usuário
try:
    from .installer import install_extension
    install_extension()
except Exception:
    pass


__version__ = "0.0.7"
__all__ = [
    "Document",
    "ParseResult",
    "Report",
    "bold",
    "inline_code",
    "italic",
    "open",
    "open_document",
    "parse",
    "parse_umd",
    "render_document",
    "save_document",
    "strike",
    "styled",
    "underline",
    "validate",
    "view",
    "__version__",
]
