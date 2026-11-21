import unittest
from pathlib import Path

from umd.document.model import Document
from umd.renderers.html import render_document

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sales_report.umd"

TEXT = """# Título

Parágrafo com **forte** e `código`.

[TABLE title="Vendas"]
Produto | Valor
--- | ---:
Notebook | R$ 12.000
[/TABLE]

[CALLOUT tone="success" title="Meta"]
Cresceu 18%.
[/CALLOUT]
"""


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.html = render_document(TEXT)

    def test_page_structure(self):
        self.assertTrue(self.html.startswith("<!DOCTYPE html>"))
        self.assertIn('<meta charset="utf-8">', self.html)
        self.assertIn("<style>", self.html)
        self.assertIn("</html>", self.html)

    def test_markdown_blocks(self):
        self.assertIn("<h1 class=\"umd-heading\">Título</h1>", self.html)
        self.assertIn("<strong>forte</strong>", self.html)
        self.assertIn("<code>código</code>", self.html)

    def test_table(self):
        self.assertIn('<table class="umd-table striped">', self.html)
        self.assertIn('<caption>Vendas</caption>', self.html)
        self.assertIn("<thead>", self.html)
        self.assertIn("<th>Produto</th>", self.html)
        self.assertIn('<td style="text-align:right">R$ 12.000</td>', self.html)
        self.assertEqual(self.html.count("<tr>"), 2)

    def test_callout_tone_and_title(self):
        self.assertIn('<aside class="umd-callout tone-success">', self.html)
        self.assertIn('<p class="umd-callout-title">Meta</p>', self.html)

    def test_escaping(self):
        html = render_document("# <script>alert(1)</script>\n\nA & B\n")
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("A &amp; B", html)

    def test_unknown_component_falls_back(self):
        html = render_document("[GRÁFICO]\nConteúdo\n[/GRÁFICO]\n")
        self.assertIn('class="umd-fallback"', html)
        self.assertIn("<p>Conteúdo</p>", html)

    def test_image(self):
        html = render_document('[IMAGE src="a.png" alt="Equipe" caption="Time" /]\n')
        self.assertIn('<img src="a.png" alt="Equipe">', html)
        self.assertIn("<figcaption>Time</figcaption>", html)

    def test_columns_layout(self):
        html = render_document("[COLUMNS gap=24]\n[CARD title=\"A\"]\nx\n[/CARD]\n[/COLUMNS]\n")
        self.assertIn("gap:24px", html)
        self.assertIn("grid-template-columns:repeat(1, minmax(0, 1fr))", html)

    def test_list_and_quote(self):
        html = render_document("- um\n- dois\n\n> citação\n")
        self.assertIn("<ul><li>um</li><li>dois</li></ul>", html)
        self.assertIn("<blockquote>citação</blockquote>", html)

    def test_example_renders_every_component(self):
        document = Document(EXAMPLE.read_text(encoding="utf-8"))
        html = render_document(document)
        for marker in ('class="umd-table', 'class="umd-callout', 'class="umd-card', 'umd-columns'):
            self.assertIn(marker, html)
        self.assertIn("Notebook Pro", html)
        self.assertNotIn("[/TABLE]", html)

    def test_fragment_mode_has_no_page_wrapper(self):
        fragment = render_document(TEXT, standalone=False)
        self.assertNotIn("<!DOCTYPE html>", fragment)
        self.assertIn("<h1", fragment)

    def test_ai_graphical_components(self):
        ai_doc = """# AI Evaluation
[CHART title="Model Benchmark" type="bar"]
GPT-4o | 88.5
Our Model | 92.1
[/CHART]

[CHART title="Latency Profile" type="column"]
2k | 14
8k | 22
[/CHART]

[CHART title="Data Mix" type="pie"]
Code | 40
Text | 60
[/CHART]

[PIPELINE title="Inference Pipeline"]
Prompt -> Tokenizer -> Transformer -> Output
[/PIPELINE]

[PROGRESS label="Fine-Tuning" value=95 max=100 /]
"""
        html = render_document(ai_doc)
        self.assertIn('class="umd-chart"', html)
        self.assertIn("Model Benchmark", html)
        self.assertIn("GPT-4o", html)
        self.assertIn('umd-column-chart', html)
        self.assertIn("Latency Profile", html)
        self.assertIn('umd-pie-chart', html)
        self.assertIn("Data Mix", html)
        self.assertIn('class="umd-pipeline"', html)
        self.assertIn("Tokenizer", html)
        self.assertIn("→", html)
        self.assertIn('class="umd-progress-card"', html)
        self.assertIn("95%", html)

    def test_curved_and_comparison_charts(self):
        doc = """
[CHART title="Loss Curve" type="curved"]
Epoch 1 | 0.85
Epoch 2 | 0.45
Epoch 3 | 0.20
[/CHART]

[CHART title="European Population" type="comparison" series="2013, 2021"]
Germany | 80.6 | 83.2
Spain | 46.6 | 47.4
[/CHART]
"""
        html = render_document(doc)
        self.assertIn('umd-curved-chart', html)
        self.assertIn('Loss Curve', html)
        self.assertIn('path fill="none"', html)
        self.assertIn('umd-comparison-chart', html)
        self.assertIn('European Population', html)
        self.assertIn('Germany', html)
        self.assertIn('80.6', html)
        self.assertIn('83.2', html)


if __name__ == "__main__":
    unittest.main()
