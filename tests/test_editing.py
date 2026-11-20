import tempfile
import unittest
from pathlib import Path

from umd.document.model import Document
from umd.document.persistence import open_document

TEXT = """# Vendas

[TABLE]
Produto | Valor
Notebook | R$ 12.000
Monitor | R$ 8.500
[/TABLE]
"""


class CellEditingTests(unittest.TestCase):
    def setUp(self):
        self.document = Document(TEXT)

    def test_set_cell_changes_only_the_cell(self):
        table = self.document.tables()[0]
        result = self.document.set_cell(table.id, 1, 1, "R$ 13.000")
        self.assertTrue(result.ok, result.message)
        self.assertEqual(self.document.grid(table.id)[1][1], "R$ 13.000")
        self.assertEqual(
            self.document.text,
            TEXT.replace("Notebook | R$ 12.000", "Notebook | R$ 13.000"),
        )
        self.assertEqual(self.document.errors(), [])

    def test_set_cell_escapes_pipes(self):
        table = self.document.tables()[0]
        self.assertTrue(self.document.set_cell(table.id, 1, 1, "A|B").ok)
        self.assertEqual(self.document.grid(table.id)[1][1], "A|B")

    def test_set_cell_rejects_newline(self):
        table = self.document.tables()[0]
        result = self.document.set_cell(table.id, 1, 0, "A\nB")
        self.assertFalse(result.ok)
        self.assertEqual(self.document.text, TEXT)

    def test_unknown_cell(self):
        table = self.document.tables()[0]
        self.assertFalse(self.document.set_cell(table.id, 9, 0, "x").ok)

    def test_append_row(self):
        table = self.document.tables()[0]
        result = self.document.append_row(table.id, ["Teclado", "R$ 4.500"])
        self.assertTrue(result.ok, result.message)
        self.assertEqual(self.document.grid(table.id)[-1], ["Teclado", "R$ 4.500"])
        self.assertTrue(self.document.text.endswith("Monitor | R$ 8.500\nTeclado | R$ 4.500\n[/TABLE]\n"))
        self.assertEqual(self.document.errors(), [])

    def test_append_row_requires_matching_width(self):
        table = self.document.tables()[0]
        self.assertFalse(self.document.append_row(table.id, ["Só uma"]).ok)

    def test_remove_row(self):
        table = self.document.tables()[0]
        self.assertTrue(self.document.remove_row(table.id, 1).ok)
        self.assertEqual(len(self.document.grid(table.id)), 2)
        self.assertIn("Monitor | R$ 8.500", self.document.text)
        self.assertNotIn("Notebook", self.document.text)

    def test_header_cannot_be_removed(self):
        table = self.document.tables()[0]
        self.assertFalse(self.document.remove_row(table.id, 0).ok)


class AttributeAndTextTests(unittest.TestCase):
    def setUp(self):
        self.document = Document('[CARD title="A"]\nTexto\n[/CARD]\n')

    def test_set_existing_attr(self):
        card = self.document.root.children[0]
        self.assertTrue(self.document.set_attr(card.id, "title", "B").ok)
        self.assertEqual(self.document.text, '[CARD title="B"]\nTexto\n[/CARD]\n')
        self.assertTrue(self.document.valid)

    def test_insert_new_attr(self):
        card = self.document.root.children[0]
        self.assertTrue(self.document.set_attr(card.id, "padding", "24").ok)
        self.assertEqual(self.document.text, '[CARD title="A" padding="24"]\nTexto\n[/CARD]\n')
        self.assertTrue(self.document.valid)

    def test_remove_attr(self):
        card = self.document.root.children[0]
        self.assertTrue(self.document.remove_attr(card.id, "title").ok)
        self.assertEqual(self.document.text, "[CARD]\nTexto\n[/CARD]\n")

    def test_rename_component(self):
        card = self.document.root.children[0]
        self.assertTrue(self.document.rename_component(card.id, "callout").ok)
        self.assertEqual(self.document.text, "[CALLOUT title=\"A\"]\nTexto\n[/CALLOUT]\n")
        self.assertTrue(self.document.valid)

    def test_set_text_on_paragraph(self):
        paragraph = self.document.root.children[0].children[0]
        self.assertTrue(self.document.set_text(paragraph.id, "Outro texto **forte**").ok)
        self.assertEqual(self.document.text, '[CARD title="A"]\nOutro texto **forte**\n[/CARD]\n')

    def test_cell_is_not_text_editable(self):
        document = Document(TEXT)
        table = document.tables()[0]
        cell = document.source_map.cell(table.id, 1, 1)
        self.assertFalse(document.set_text(cell.id, "x").ok)


class HistoryTests(unittest.TestCase):
    def test_undo_and_redo(self):
        document = Document(TEXT)
        table = document.tables()[0]
        document.set_cell(table.id, 1, 1, "R$ 13.000")
        self.assertTrue(document.history.can_undo)

        self.assertTrue(document.undo())
        self.assertEqual(document.text, TEXT)
        self.assertTrue(document.history.can_redo)
        self.assertEqual(document.grid(table.id)[1][1], "R$ 12.000")

        self.assertTrue(document.redo())
        self.assertEqual(document.grid(table.id)[1][1], "R$ 13.000")

    def test_undo_without_history(self):
        self.assertFalse(Document(TEXT).undo())


class PersistenceTests(unittest.TestCase):
    def test_save_and_reopen(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "doc.umd"
            path.write_text(TEXT, encoding="utf-8", newline="")

            document = open_document(path)
            table = document.tables()[0]
            self.assertTrue(document.set_cell(table.id, 1, 1, "R$ 13.000").ok)
            document.save()

            reopened = open_document(path)
            self.assertEqual(reopened.grid(table.id)[1][1], "R$ 13.000")
            self.assertTrue(reopened.valid)
            self.assertEqual(reopened.check_spans(), [])

    def test_crlf_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "doc.umd"
            original = TEXT.replace("\n", "\r\n")
            path.write_bytes(original.encode("utf-8"))

            document = open_document(path)
            table = document.tables()[0]
            document.set_cell(table.id, 1, 1, "R$ 13.000")
            document.save()

            self.assertIn(b"\r\n", path.read_bytes())
            self.assertNotIn(b"\r\r\n", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
