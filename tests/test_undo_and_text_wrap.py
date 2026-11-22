from pathlib import Path
from playwright.sync_api import sync_playwright

EDITOR_HTML = Path(__file__).resolve().parent.parent / "editor.html"


def test_ctrl_z_undo_and_redo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{str(EDITOR_HTML).replace(chr(92), '/')}")

        page.evaluate("(text) => renderDocument(text)", "# Title\n\nOriginal paragraph")
        assert "Original paragraph" in page.evaluate("() => serializeDocument()")

        # Modify paragraph and trigger save
        page.evaluate("""() => {
            const p = document.querySelector('p');
            p.innerText = 'Modified paragraph';
            p.dispatchEvent(new Event('input', { bubbles: true }));
        }""")
        page.wait_for_timeout(200)
        assert "Modified paragraph" in page.evaluate("() => serializeDocument()")

        # Press Ctrl+Z -> should revert to Original paragraph
        page.keyboard.press("Control+z")
        page.wait_for_timeout(100)
        after_undo = page.evaluate("() => serializeDocument()")
        assert "Original paragraph" in after_undo
        assert "Modified paragraph" not in after_undo

        # Press Ctrl+Y -> should redo back to Modified paragraph
        page.keyboard.press("Control+y")
        page.wait_for_timeout(100)
        after_redo = page.evaluate("() => serializeDocument()")
        assert "Modified paragraph" in after_redo

        browser.close()


def test_plain_text_block_wraps_without_horizontal_scroll():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 700})
        page.goto(f"file:///{str(EDITOR_HTML).replace(chr(92), '/')}")

        long_line = "Use TestCase com setUpTestData e force_login no Client. " * 10
        sample = f"```text\n[ESPERADO]\n{long_line}\n```\n\n```python\nx = {'a' * 120!r}\n```\n"
        page.evaluate("(text) => renderDocument(text)", sample)

        metrics = page.evaluate("""() => {
            const blocks = Array.from(document.querySelectorAll('.notion-code-block'));
            return blocks.map(b => {
                const content = b.querySelector('.notion-code-content');
                const cs = getComputedStyle(content);
                return {
                    hasWrapClass: b.classList.contains('is-text-wrap'),
                    whiteSpace: cs.whiteSpace,
                    scrollWidth: content.scrollWidth,
                    clientWidth: content.clientWidth,
                };
            });
        }""")

        assert len(metrics) == 2
        # First block is TEXT -> wraps without horizontal overflow
        assert metrics[0]["hasWrapClass"] is True
        assert metrics[0]["whiteSpace"] == "pre-wrap"
        assert metrics[0]["scrollWidth"] <= metrics[0]["clientWidth"] + 2

        # Second block is Python -> preserves standard code formatting
        assert metrics[1]["hasWrapClass"] is False
        assert metrics[1]["whiteSpace"] == "pre"

        browser.close()
