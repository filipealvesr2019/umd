import unittest

from umd.core.parser import parse
from umd.core.validator import validate

TABLE = """# Título

[TABLE title="Vendas"]
Produto | Valor
Notebook | R$ 12.000
Monitor | R$ 8.500
[/TABLE]
"""


class MarkdownBlockTests(unittest.TestCase):
    def test_heading_and_paragraph(self):
        result = parse("# Título\n\nParágrafo **forte**.\n")
        types = [node.type for node in result.root.children]
        self.assertEqual(types, ["heading", "paragraph"])
        heading = result.root.children[0]
        self.assertEqual(heading.text, "Título")
        self.assertEqual(heading.props["level"], 1)
        paragraph = result.root.children[1]
        self.assertEqual([child.type for child in paragraph.children], ["text", "strong", "text"])
        self.assertEqual(paragraph.children[1].text, "forte")

    def test_list_quote_and_code(self):
        text = "- um\n- dois\n\n> citação\n\n```py\nprint(1)\n```\n"
        result = parse(text)
        types = [node.type for node in result.root.children]
        self.assertEqual(types, ["list", "quote", "code_block"])
        self.assertEqual(len(result.root.children[0].children), 2)
        self.assertEqual(result.root.children[2].props["lang"], "py")
        self.assertEqual(result.root.children[2].text, "print(1)")

    def test_comment_is_preserved(self):
        result = parse("<!-- nota -->\ntexto\n")
        self.assertEqual(result.root.children[0].type, "comment")
        self.assertEqual(result.root.children[0].text, "<!-- nota -->")

    def test_multiline_paragraph(self):
        result = parse("linha um\nlinha dois\n")
        paragraph = result.root.children[0]
        self.assertEqual(paragraph.text, "linha um\nlinha dois")


class ComponentTests(unittest.TestCase):
    def test_table_structure(self):
        result = parse(TABLE)
        table = result.root.children[1]
        self.assertEqual(table.name, "TABLE")
        rows = [child for child in table.children if child.type == "table_row"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[0].props["header"])
        self.assertEqual(rows[1].props["row"], 1)
        self.assertEqual([cell.text for cell in rows[1].children], ["Notebook", "R$ 12.000"])
        self.assertEqual(validate(result.root), [])

    def test_alignment_row_is_not_a_data_row(self):
        text = "[TABLE]\nA | B\n--- | ---:\n1 | 2\n[/TABLE]\n"
        result = parse(text)
        table = result.root.children[0]
        rows = [child for child in table.children if child.type == "table_row"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[1].props["align"])
        self.assertIsNone(rows[1].props["row"])
        self.assertEqual(rows[2].props["row"], 1)
        self.assertEqual(validate(result.root), [])

    def test_attributes(self):
        text = '[CARD title="Receita" tone=info padding=24 ativo]\nTexto\n[/CARD]\n'
        result = parse(text)
        card = result.root.children[0]
        attrs = {key: attr.value for key, attr in card.meta["attrs"].items()}
        self.assertEqual(attrs, {"title": "Receita", "tone": "info", "padding": "24", "ativo": None})
        self.assertEqual(card.children[0].type, "paragraph")

    def test_nested_components(self):
        text = "[COLUMNS gap=16]\n[CARD title=\"A\"]\nOi\n[/CARD]\n[/COLUMNS]\n"
        result = parse(text)
        columns = result.root.children[0]
        self.assertEqual(columns.name, "COLUMNS")
        self.assertEqual(columns.children[0].name, "CARD")
        self.assertEqual(columns.end - columns.start, len(text.rstrip("\n")))

    def test_self_closing(self):
        result = parse('[IMAGE src="a.png" alt="A" /]\n')
        image = result.root.children[0]
        self.assertEqual(image.name, "IMAGE")
        self.assertTrue(image.meta["self_closing"])
        self.assertFalse(image.children)

    def test_case_insensitive_names(self):
        result = parse("[card]\nOi\n[/card]\n")
        self.assertEqual(result.root.children[0].name, "CARD")
        self.assertEqual([d for d in result.diagnostics if d.level == "error"], [])


class DiagnosticTests(unittest.TestCase):
    def test_unclosed_component(self):
        result = parse("[CARD]\nTexto\n")
        codes = [d.code for d in result.diagnostics]
        self.assertIn("E_UNCLOSED", codes)

    def test_unknown_component(self):
        result = parse("[GRÁFICO]\nx\n[/GRÁFICO]\n")
        codes = [d.code for d in result.diagnostics]
        self.assertIn("E_UNKNOWN_COMPONENT", codes)

    def test_stray_close(self):
        result = parse("[/CARD]\n")
        self.assertIn("E_STRAY_CLOSE", [d.code for d in result.diagnostics])

    def test_column_count(self):
        text = "[TABLE]\nA | B\n1 | 2 | 3\n[/TABLE]\n"
        diagnostics = validate(parse(text).root)
        self.assertIn("E_COLUMN_COUNT", [d.code for d in diagnostics])

    def test_required_prop(self):
        diagnostics = validate(parse("[IMAGE alt=\"sem src\" /]\n").root)
        self.assertIn("E_REQUIRED_PROP", [d.code for d in diagnostics])

    def test_unknown_prop_is_warning(self):
        diagnostics = validate(parse('[CARD foo="x"]\nOi\n[/CARD]\n').root)
        self.assertIn("W_UNKNOWN_PROP", [d.code for d in diagnostics])
        self.assertTrue(all(d.level == "warning" for d in diagnostics))

    def test_unclosed_fence(self):
        result = parse("```\naberto\n")
        self.assertIn("E_UNCLOSED_FENCE", [d.code for d in result.diagnostics])


class LexerTests(unittest.TestCase):
    def test_spans_are_contiguous(self):
        text = "# A\n\n[TABLE]\nX | Y\n1 | 2\n[/TABLE]\n"
        tokens = parse(text).tokens
        positions = [(token.start, token.end) for token in tokens[:-1]]
        for current, following in zip(positions, positions[1:]):
            self.assertLessEqual(current[1], following[0])

    def test_escaped_bracket_is_text(self):
        result = parse("\\[CARD] não é tag\n")
        self.assertEqual(result.root.children[0].type, "paragraph")


if __name__ == "__main__":
    unittest.main()
