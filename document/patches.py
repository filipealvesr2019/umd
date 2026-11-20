"""Patches: substituições de intervalos exatos do texto original."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Patch:
    start: int
    end: int
    replacement: str
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "span": [self.start, self.end],
            "replacement": self.replacement,
            "label": self.label,
        }


class PatchError(Exception):
    pass


def apply_patches(text: str, patches: list[Patch]) -> str:
    """Aplica patches validando limites e sobreposição.

    A ordem de aplicação é decrescente por offset, então cada patch é
    aplicado sobre o texto ainda não deslocado pelos anteriores.
    """
    if not patches:
        return text
    ordered = sorted(patches, key=lambda p: (p.start, p.end), reverse=True)
    previous_start = len(text) + 1
    for patch in ordered:
        if patch.start < 0 or patch.end < patch.start or patch.end > len(text):
            raise PatchError(
                f"patch fora dos limites: [{patch.start}, {patch.end}) em texto de {len(text)} caracteres"
            )
        if patch.end > previous_start:
            raise PatchError(
                f"patches sobrepostos em [{patch.start}, {patch.end})"
            )
        previous_start = patch.start
    result = text
    for patch in ordered:
        result = result[: patch.start] + patch.replacement + result[patch.end :]
    return result


@dataclass
class EditResult:
    ok: bool = False
    message: str = ""
    text: str = ""
    patches: list[Patch] = field(default_factory=list)
    diagnostics: list[Any] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "message": self.message,
            "patches": [p.to_dict() for p in self.patches],
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }
