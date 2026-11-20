"""Leitura e escrita de arquivos ``.umd``."""
from __future__ import annotations

from pathlib import Path

from .model import Document, read_text

EXTENSION = ".umd"
VALID_EXTENSIONS = (".umd",)


def open_document(path: str | Path) -> Document:
    target = Path(path)
    if target.suffix.lower() not in VALID_EXTENSIONS:
        raise ValueError(f"esperado um arquivo .umd, recebido '{target.name}'")
    return Document(read_text(target), target)


def save_document(document: Document, path: str | Path | None = None) -> Path:
    return document.save(path)


def read(path: str | Path) -> str:
    return read_text(path)
