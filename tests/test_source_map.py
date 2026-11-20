import unittest
from pathlib import Path

from umd.document.model import Document

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sales_report.umd"

TEXT = """# Título

Parágrafo simples.

[TABLE]
Produto | Valor
Notebook | R$ 12.000
[/TABLE]
"""


class SourceMapTests(unittest.TestCase):
    def setUp(self):
        self.document = Document(TEXT)

    def test_no_span_diagnostics(self):
        self.assertEqual(self.document.check_spans(), [])

    def test_node_slices_match_text(self):
        for node in self.document.nodes():
            if node.type in ("heading", "paragraph"):
                self.assertEqual(
                    self.document.text[node.meta["text_start"] : node.meta["text_end"]],
                    node.text,
                )

    def test_cell_spans_point_to_the_cell_text(self):
        table = self.document.tables()[0]
        for row, cells in enumerate(self.document.grid(table.id)):
            for col, value in enumerate(cells):
                cell = self.document.source_map.cell(table.id, row, col)
                self.assertIsNotNone(cell)
                self.assertEqual(self.document.text[cell.start : cell.end], cell.text)

    def test_node_at(self):
        offset = self.document.text.index("Notebook")
        node = self.document.source_map.node_at(offset)
        self.assertEqual(node.type, "table_cell")
        self.assertEqual(node.text, "Notebook")

    def test_example_file_has_consistent_spans(self):
        document = Document(EXAMPLE.read_text(encoding="utf-8"))
        self.assertEqual(document.check_spans(), [])
        self.assertTrue(document.valid, [str(d) for d in document.errors()])

    def test_editora_is_the_more_specific_node(self):
        offset = self.document.text.index("Parágrafo")
        node = self.document.source_map.node_at(offset)
        self.assertEqual(node.type, "paragraph")


if __name__ == "__main__":
    unittest.main()
