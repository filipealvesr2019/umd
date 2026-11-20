"""Document Model: o documento editável, ligado ao texto original.

O texto é a fonte da verdade. Toda edição visual é traduzida em um ``Patch``
sobre um intervalo exato; depois de aplicar, o documento é reprocessado, de
modo que AST, source map e texto nunca divergem.
"""
from __future__ import annotations

from pathlib import Path

from ..components import registry
from ..components import table as table_component
from ..core.ast import Node
from ..core.parser import parse
from ..core.validator import validate
from .history import History
from .patches import EditResult, Patch, PatchError, apply_patches
from .source_map import SourceMap

EDITABLE_TYPES = ("heading", "paragraph", "quote", "list_item", "code_block")


class Document:
    def __init__(self, text: str = "", path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.history = History(self.text)
        self._parse()

    # -- ciclo de vida ----------------------------------------------
    def _parse(self) -> None:
        result = parse(self.text)
        self.root = result.root
        self.parser_diagnostics = list(result.diagnostics)
        self.source_map = SourceMap.from_root(self.root)
        self.diagnostics = _sorted(result.diagnostics + validate(self.root))

    def reload(self) -> None:
        if self.path and self.path.exists():
            raw = read_text(self.path)
            self.text = raw.replace("\r\n", "\n").replace("\r", "\n")
            self.newline = "\r\n" if "\r\n" in raw else "\n"
            self.history = History(self.text)
            self._parse()

    @property
    def valid(self) -> bool:
        return not [d for d in self.diagnostics if d.level == "error"]

    def errors(self):
        return [d for d in self.diagnostics if d.level == "error"]

    def warnings(self):
        return [d for d in self.diagnostics if d.level == "warning"]

    def check_spans(self):
        return self.source_map.check(self.text)

    # -- consultas --------------------------------------------------
    def node(self, node_id: str) -> Node | None:
        return self.root.find(node_id)

    def nodes(self) -> list[Node]:
        return list(self.root.walk())

    def tables(self) -> list[Node]:
        return [n for n in self.root.walk() if n.is_component and n.name == "TABLE"]

    def table(self, table_id: str) -> Node:
        node = self.root.find(table_id)
        if node is None:
            raise KeyError(f"nó '{table_id}' não existe")
        if not node.is_component or node.name != "TABLE":
            raise KeyError(f"'{table_id}' não é uma TABLE")
        return node

    def grid(self, table_id: str) -> list[list[str]]:
        return table_component.grid(self.table(table_id))

    def source(self) -> str:
        """Texto do documento no estilo de quebra de linha original."""
        if self.newline == "\n":
            return self.text
        return self.text.replace("\n", self.newline)

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else self.path
        if target is None:
            raise ValueError("documento sem caminho: informe path")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        with open(temporary, "w", encoding="utf-8", newline="") as handle:
            handle.write(self.source())
        temporary.replace(target)
        self.path = target
        return target

    # -- edições ----------------------------------------------------
    def set_cell(self, table_id: str, row: int, col: int, value: str) -> EditResult:
        try:
            self.table(table_id)
        except KeyError as exc:
            return _fail(str(exc))
        cell = self.source_map.cell(table_id, row, col)
        if cell is None:
            return _fail(f"célula ({row}, {col}) não existe em {table_id}")
        clean = str(value).strip()
        if "\n" in clean or "\r" in clean:
            return _fail("uma célula não pode conter quebra de linha")
        clean = clean.replace("|", "\\|")
        patch = Patch(cell.start, cell.end, clean, f"célula {row},{col}")
        return self._commit([patch], f"editar célula ({row}, {col})")

    def set_cell_text(self, cell_id: str, value: str) -> EditResult:
        node = self.node(cell_id)
        if node is None or node.type != "table_cell":
            return _fail(f"'{cell_id}' não é uma célula")
        clean = str(value).strip().replace("|", "\\|")
        if "\n" in clean:
            return _fail("uma célula não pode conter quebra de linha")
        return self._commit([Patch(node.start, node.end, clean, cell_id)], f"editar {cell_id}")

    def append_row(self, table_id: str, values: list[str]) -> EditResult:
        return self.insert_row(table_id, -1, values)

    def insert_row(self, table_id: str, index: int, values: list[str]) -> EditResult:
        try:
            table = self.table(table_id)
        except KeyError as exc:
            return _fail(str(exc))
        rows = table_component.data_rows(table)
        if not rows:
            return _fail("[TABLE] sem cabeçalho: não é possível inserir linhas")
        width = len(rows[0].children)
        if len(values) != width:
            return _fail(f"esperadas {width} células, recebidas {len(values)}")
        for value in values:
            if "\n" in str(value):
                return _fail("uma célula não pode conter quebra de linha")
        position = rows[-1] if index < 0 or index >= len(rows) else rows[index]
        indent = " " * max(0, position.column - 1)
        line = table_component.format_row([str(v) for v in values], table_component.row_style(table))
        patch = Patch(position.end, position.end, f"\n{indent}{line}", "inserir linha")
        return self._commit([patch], f"inserir linha em {table_id}")

    def remove_row(self, table_id: str, index: int) -> EditResult:
        try:
            table = self.table(table_id)
        except KeyError as exc:
            return _fail(str(exc))
        rows = table_component.data_rows(table)
        if index <= 0:
            return _fail("a linha 0 é o cabeçalho e não pode ser removida")
        if index >= len(rows):
            return _fail(f"linha {index} não existe (a tabela tem {len(rows)} linhas)")
        row = rows[index]
        end = row.end + 1 if self.text[row.end : row.end + 1] == "\n" else row.end
        return self._commit([Patch(row.start, end, "", f"linha {index}")], f"remover linha {index}")

    def set_text(self, node_id: str, value: str) -> EditResult:
        node = self.node(node_id)
        if node is None:
            return _fail(f"nó '{node_id}' não existe")
        if node.type not in EDITABLE_TYPES:
            return _fail(f"'{node.type}' não é editável como texto (use set_cell/set_attr)")
        return self._commit([Patch(node.start, node.end, value, node_id)], f"editar {node_id}")

    def set_attr(self, node_id: str, key: str, value: str | None = None) -> EditResult:
        node = self.node(node_id)
        if node is None:
            return _fail(f"nó '{node_id}' não existe")
        if not node.is_component:
            return _fail(f"'{node_id}' não é um componente")
        if value is None:
            return self.remove_attr(node_id, key)
        clean = str(value)
        if '"' in clean or "\n" in clean:
            return _fail("valor de atributo não pode conter aspas duplas ou quebra de linha")
        attr = node.meta.get("attrs", {}).get(key)
        if attr is not None and attr.value_start is not None:
            patch = Patch(attr.value_start, attr.value_end, clean, f"attr {key}")
        elif attr is not None:
            patch = Patch(attr.start, attr.end, f'{key}="{clean}"', f"attr {key}")
        else:
            position = node.meta.get("attr_insert_at", node.end - 1)
            patch = Patch(position, position, f' {key}="{clean}"', f"attr {key}")
        return self._commit([patch], f"definir {key}={clean!r} em {node_id}")

    def remove_attr(self, node_id: str, key: str) -> EditResult:
        node = self.node(node_id)
        if node is None or not node.is_component:
            return _fail(f"'{node_id}' não é um componente")
        attr = node.meta.get("attrs", {}).get(key)
        if attr is None:
            return _fail(f"'{node_id}' não tem o atributo '{key}'")
        start = attr.start
        while start > 0 and self.text[start - 1] in " \t":
            start -= 1
        return self._commit([Patch(start, attr.end, "", f"attr {key}")], f"remover {key} de {node_id}")

    def rename_component(self, node_id: str, new_name: str) -> EditResult:
        node = self.node(node_id)
        if node is None or not node.is_component:
            return _fail(f"'{node_id}' não é um componente")
        name = new_name.upper()
        if not registry.exists(name):
            return _fail(f"componente [{name}] desconhecido")
        patches: list[Patch] = []
        opening = node.meta.get("open_name_span")
        closing = node.meta.get("close_name_span")
        if opening:
            patches.append(Patch(opening[0], opening[1], name, "abertura"))
        if closing:
            patches.append(Patch(closing[0], closing[1], name, "fechamento"))
        if not patches:
            return _fail(f"não foi possível localizar o nome de {node_id}")
        return self._commit(patches, f"renomear {node_id} para {name}")

    # -- undo / redo ------------------------------------------------
    def undo(self) -> bool:
        step = self.history.undo()
        if step is None:
            return False
        self.text = step.before
        self._parse()
        return True

    def redo(self) -> bool:
        step = self.history.redo()
        if step is None:
            return False
        self.text = step.after
        self._parse()
        return True

    # -- interno ----------------------------------------------------
    def _commit(self, patches: list[Patch], label: str) -> EditResult:
        try:
            new_text = apply_patches(self.text, patches)
        except PatchError as exc:
            return _fail(str(exc))
        before = self.text
        self.text = new_text
        self._parse()
        self.history.record(label, before, new_text)
        result = EditResult(ok=True, message=label, text=new_text, patches=patches)
        result.diagnostics = self.errors()
        return result


def _fail(message: str) -> EditResult:
    return EditResult(ok=False, message=message)


def _sorted(diagnostics):
    return sorted(diagnostics, key=lambda d: (d.line, d.column, d.code))


def read_text(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()
