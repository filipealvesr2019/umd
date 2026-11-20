import unittest
from pathlib import Path

from umd.core.parser import parse
from umd.document.model import Document

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sales_report.umd"


class RoundTripTests(unittest.TestCase):
    def test_parse_does_not_change_the_text(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        document = Document(text)
        self.assertEqual(document.text, text)

    def test_reserialization_is_identity(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        document = Document(text)
        self.assertEqual(document.source(), text)

    def test_example_is_valid(self):
        document = Document(EXAMPLE.read_text(encoding="utf-8"))
        self.assertTrue(document.valid, [str(d) for d in document.errors()])
        self.assertEqual(document.check_spans(), [])

    def test_reparse_is_stable(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        first = parse(text)
        second = parse(text)
        self.assertEqual(
            [node.to_dict() for node in first.root.children],
            [node.to_dict() for node in second.root.children],
        )

    def test_edits_keep_document_parseable(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        document = Document(text)
        table = document.tables()[0]
        self.assertTrue(document.set_cell(table.id, 2, 1, "90").ok)
        self.assertTrue(document.append_row(table.id, ["Mouse", "40", "R$ 3.200"]).ok)
        self.assertTrue(document.valid, [str(d) for d in document.errors()])
        self.assertEqual(document.check_spans(), [])
        self.assertEqual(document.source().count("[/TABLE]"), 1)

    def test_comment_and_blank_lines_survive_edits(self):
        text = EXAMPLE.read_text(encoding="utf-8")
        document = Document(text)
        table = document.tables()[0]
        document.set_cell(table.id, 1, 1, "121")
        self.assertIn("<!-- This comment is preserved across all edits. -->", document.text)
        self.assertIn("\n\n", document.text)

    def test_no_overlapping_patches(self):
        document = Document(EXAMPLE.read_text(encoding="utf-8"))
        table = document.tables()[0]
        self.assertTrue(document.set_attr(table.id, "title", "Vendas 2026").ok)
        self.assertTrue(document.set_cell(table.id, 1, 1, "130").ok)
        self.assertTrue(document.valid)


if __name__ == "__main__":
    unittest.main()
