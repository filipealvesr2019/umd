"""Document Model, source mapping, patches e histórico."""
from .history import History, Step
from .model import Document
from .patches import EditResult, Patch, PatchError, apply_patches
from .persistence import open_document, save_document
from .source_map import SourceMap

__all__ = [
    "Document",
    "EditResult",
    "History",
    "Patch",
    "PatchError",
    "SourceMap",
    "Step",
    "apply_patches",
    "open_document",
    "save_document",
]
