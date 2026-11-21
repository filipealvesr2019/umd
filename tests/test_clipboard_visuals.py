import os
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_clipboard_visual_elements_copy():
    editor_path = os.path.abspath("G:/umd/editor.html")
    model_card_path = os.path.abspath("G:/umd/examples/ai_model_card.umd")
    with open(model_card_path, "r", encoding="utf-8") as f:
        content = f.read()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(f"file:///{editor_path.replace(os.sep, '/')}")
        await page.wait_for_selector("#editor-page")
        await page.evaluate("(c) => renderDocument(c)", content)

        # 1. Test full page copy (Ctrl+A simulation)
        await page.keyboard.press("Control+A")
        full_res = await page.evaluate("""() => {
            const pageEl = document.getElementById('editor-page');
            return exportCleanClipboard(pageEl);
        }""")

        # Verify no UI buttons in full copy
        assert "✕ Delete" not in full_res["html"]
        assert "✕ Delete" not in full_res["text"]
        assert "delete-stage-btn" not in full_res["html"]
        assert "×" not in full_res["text"]  # stage delete icon
        assert "<table" in full_res["html"]  # cards converted to table
        assert "| PARAMETERS |" in full_res["text"] or "PARAMETERS" in full_res["text"]

        # 2. Test partial selection of cards
        partial_res = await page.evaluate("""() => {
            const colBlock = document.querySelector('.isolated-element[data-block-type="columns"]');
            const range = document.createRange();
            range.selectNodeContents(colBlock);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);

            const container = document.createElement('div');
            container.appendChild(range.cloneContents());
            return exportCleanClipboard(container);
        }""")

        assert "✕ Delete" not in partial_res["html"]
        assert "✕ Delete" not in partial_res["text"]
        assert "<table" in partial_res["html"]

        # 3. Test pipeline clean export
        pipe_res = await page.evaluate("""() => {
            const pipeBlock = document.querySelector('.isolated-element[data-block-type="pipeline"]');
            const range = document.createRange();
            range.selectNodeContents(pipeBlock);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);

            const container = document.createElement('div');
            container.appendChild(range.cloneContents());
            return exportCleanClipboard(container);
        }""")

        assert "✕ Delete" not in pipe_res["html"]
        assert "delete-stage-btn" not in pipe_res["html"]
        assert "➔" in pipe_res["html"] or "➔" in pipe_res["text"]

        await browser.close()
