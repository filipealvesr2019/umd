"""Histórico de edições (undo/redo) sobre snapshots de texto."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Step:
    label: str
    before: str
    after: str


class History:
    def __init__(self, initial: str) -> None:
        self._undo: list[Step] = []
        self._redo: list[Step] = []

    def record(self, label: str, before: str, after: str) -> None:
        if before == after:
            return
        self._undo.append(Step(label, before, after))
        self._redo.clear()

    def undo(self) -> Step | None:
        if not self._undo:
            return None
        step = self._undo.pop()
        self._redo.append(step)
        return step

    def redo(self) -> Step | None:
        if not self._redo:
            return None
        step = self._redo.pop()
        self._undo.append(step)
        return step

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    @property
    def undo_label(self) -> str:
        return self._undo[-1].label if self._undo else ""

    @property
    def redo_label(self) -> str:
        return self._redo[-1].label if self._redo else ""

    def labels(self) -> list[str]:
        return [step.label for step in self._undo]
