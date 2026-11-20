import unittest

from umd.core.parser import parse
from umd.renderers.html import render_document


class SecurityTests(unittest.TestCase):
    def test_xss_in_markdown_content_is_escaped(self):
        malicious = """# <script>alert('xss-heading')</script>

<script>alert('xss-p')</script>

- <script>alert('xss-list')</script>

> <script>alert('xss-quote')</script>

`alert('<xss-code>')`
"""
        html = render_document(malicious)
        self.assertNotIn("<script>", html)
        self.assertNotIn("</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;/script&gt;", html)

    def test_javascript_urls_in_links_are_neutralized(self):
        malicious = """[Click for exploit](javascript:alert(document.cookie))
[VBScript exploit](vbscript:msgbox(1))
[Data exploit](data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==)
[Safe link](https://example.com/docs)
"""
        html = render_document(malicious)
        self.assertNotIn('href="javascript:', html.lower())
        self.assertNotIn('href="vbscript:', html.lower())
        self.assertNotIn('href="data:text/html', html.lower())
        self.assertIn('href="https://example.com/docs"', html)

    def test_component_attribute_injection_is_safe(self):
        doc = """[CALLOUT tone='"><script>alert(1)</script>' title='<img src=x onerror=alert(2)>']
Body text with <svg onload=alert(3)>
[/CALLOUT]

[CARD title='"><b onmouseover=alert(4)>Card</b>']
Card content
[/CARD]

[PROGRESS label='"><script>alert(5)</script>' value="50" max="100" /]

[CHART title='"><script>alert(6)</script>' type="bar"]
Label <script> | 80
[/CHART]
"""
        html = render_document(doc)
        # Ensure no active unescaped HTML tags were injected into attributes or DOM
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img", html)
        self.assertNotIn("<svg", html)
        self.assertNotIn("<b ", html)
        # All brackets must be properly entity-escaped
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img", html)
        self.assertIn("&lt;svg", html)

    def test_malformed_syntax_does_not_crash_parser(self):
        unclosed = """[CALLOUT tone="success"]
[CHART title="Unclosed Chart" type="bar"]
Row 1 | 50
"""
        res = parse(unclosed)
        self.assertIsNotNone(res.root)

        # Parser handles unclosed blocks gracefully and records diagnostics
        self.assertTrue(any(d.code == "E_UNCLOSED" for d in res.diagnostics))

    def test_extreme_values_and_fuzzing(self):
        fuzz = """[CHART title="Stress Test" type="bar"]
Item A | -999999999999999999999999999999999999999999999999999999999999
Item B | NaN
Item C | Infinity
Item D | not_a_number
Item E | 0
[/CHART]

[PROGRESS label="Progress Stress" value="-500" max="0" /]
"""
        html = render_document(fuzz)
        self.assertIn("Stress Test", html)
        self.assertIn("Progress Stress", html)

    def test_unicode_and_special_characters_preserved(self):
        unicode_doc = """# Teste 🚀 com acentuação e símbolos: 日本語, Español, Ç, ã, é, ⚡

[CALLOUT tone="info" title="Equação: α + β = γ"]
Fórmula: $E = mc^2$ e símbolos & < > " '
[/CALLOUT]
"""
        html = render_document(unicode_doc)
        self.assertIn("🚀", html)
        self.assertIn("日本語", html)
        self.assertIn("Español", html)
        self.assertIn("Ç", html)
        self.assertIn("α + β = γ", html)


if __name__ == "__main__":
    unittest.main()
