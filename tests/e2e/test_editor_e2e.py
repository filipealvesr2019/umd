"""End-to-end tests for the UMD visual editor (editor.html)."""

BASE_DOC = "# Title\n\nOriginal paragraph\n"

CHART_DOC = """# Chart Demo

[CHART title="Benchmark (%)" type="bar"]
Alpha | 88.5
Beta | 92.4
[/CHART]
"""

TABLE_DOC = """[TABLE title="Vendas"]
Produto | Valor
Notebook | 12000
[/TABLE]
"""


def _serialize(page) -> str:
    return page.evaluate("() => serializeDocument()")


def test_render_and_serialize_roundtrip(page):
    page.evaluate("(text) => renderDocument(text)", BASE_DOC)
    output = _serialize(page)
    assert "# Title" in output
    assert "Original paragraph" in output
    assert page.locator("#editor-page h1").count() == 1


def test_insert_heading_block(page):
    page.evaluate("(text) => renderDocument(text)", BASE_DOC)
    page.evaluate("() => insertFromMenu('add-h2')")
    page.wait_for_timeout(150)
    output = _serialize(page)
    assert "##" in output


def test_edit_paragraph_and_undo_redo(page):
    page.evaluate("(text) => renderDocument(text)", BASE_DOC)
    page.evaluate(
        """() => {
            const p = document.querySelector('#editor-page p');
            p.innerText = 'Edited paragraph';
            p.dispatchEvent(new Event('input', { bubbles: true }));
        }"""
    )
    page.wait_for_timeout(200)
    assert "Edited paragraph" in _serialize(page)

    page.keyboard.press("Control+z")
    page.wait_for_timeout(150)
    after_undo = _serialize(page)
    assert "Original paragraph" in after_undo
    assert "Edited paragraph" not in after_undo

    page.keyboard.press("Control+y")
    page.wait_for_timeout(150)
    assert "Edited paragraph" in _serialize(page)


def test_light_theme_class_is_applied(page):
    page.evaluate("() => document.body.classList.add('vscode-light')")
    page.wait_for_timeout(100)
    background = page.evaluate(
        "() => getComputedStyle(document.body).backgroundColor"
    )
    assert background not in ("", "rgba(0, 0, 0, 0)")
    assert page.evaluate("() => document.body.classList.contains('vscode-light')")


def test_chart_document_renders_chart_block(page):
    page.evaluate("(text) => renderDocument(text)", CHART_DOC)
    assert page.locator("#editor-page .notion-chart-block").count() == 1
    assert "Benchmark" in page.inner_text("#editor-page")


def test_table_document_renders_rows(page):
    page.evaluate("(text) => renderDocument(text)", TABLE_DOC)
    assert page.locator("#editor-page table").count() == 1
    assert "Notebook" in page.inner_text("#editor-page")


def test_image_block_renders_without_base64_bloat(page):
    page.evaluate("(text) => renderDocument(text)", "![Plot](./plot.png)\n")
    assert page.locator("#editor-page img").count() == 1
    assert "data:image" not in _serialize(page)
