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


def test_image_block_render_resize_and_roundtrip():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 700})
        page.goto(f"file:///{str(EDITOR_HTML).replace(chr(92), '/')}")

        sample = (
            '[IMAGE src="assets/screenshot_01_editor_overview.png" '
            'alt="Overview" caption="Figura 1" width="640" /]\n\n'
            '![Plot](./plot.png)\n'
        )
        page.evaluate("(text) => renderDocument(text)", sample)

        assert page.locator('.notion-image-block').count() == 2
        assert page.locator('.notion-image-caption').first.inner_text().strip() == "Figura 1"

        # Hover first image and click width preset 'L' (820px)
        first_img_wrap = page.locator('.isolated-element[data-block-type="image"]').first
        first_img_wrap.hover()
        first_img_wrap.get_by_role("button", name="L", exact=True).click()

        serialized = page.evaluate("() => serializeDocument()")
        assert 'src="assets/screenshot_01_editor_overview.png"' in serialized
        assert 'caption="Figura 1"' in serialized
        assert 'width="820"' in serialized
        assert 'src="./plot.png"' in serialized

        browser.close()


def test_light_and_dark_theme_palettes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 700})
        page.goto(f"file:///{str(EDITOR_HTML).replace(chr(92), '/')}")
        page.evaluate("(text) => renderDocument(text)", "# Title\n\n```python\nx = 1\n```\n")

        # Force dark mode (default VS Code dark)
        page.evaluate("() => { document.body.className = 'vscode-dark'; }")
        dark_vars = page.evaluate("""() => {
            const cs = getComputedStyle(document.body);
            const code = getComputedStyle(document.querySelector('.notion-code-block'));
            return { text: cs.getPropertyValue('--text-primary').trim(), codeBg: code.backgroundColor };
        }""")
        assert dark_vars["text"] == "#bec4cc"
        assert dark_vars["codeBg"] == "rgb(24, 24, 24)"

        # Switch to VS Code light theme
        page.evaluate("() => { document.body.className = 'vscode-light'; }")
        light_vars = page.evaluate("""() => {
            const cs = getComputedStyle(document.body);
            const code = getComputedStyle(document.querySelector('.notion-code-block'));
            return { text: cs.getPropertyValue('--text-primary').trim(), codeBg: code.backgroundColor };
        }""")
        assert light_vars["text"] == "#1f2937"
        assert light_vars["codeBg"] == "rgb(248, 250, 252)"

        browser.close()
