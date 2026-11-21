import os
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_add_element_exact_click_position():
    editor_path = os.path.abspath("G:/umd/editor.html")
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(f"file:///{editor_path.replace(os.sep, '/')}")
        await page.wait_for_selector("#editor-page")

        # Load document with "# Heading 1"
        await page.evaluate("renderDocument('# Heading 1')")

        blocks_before = await page.evaluate("""() => {
            return Array.from(document.getElementById('editor-page').children).map(c => ({
                tag: c.tagName,
                type: c.getAttribute('data-block-type'),
                text: c.innerText.trim()
            }));
        }""")
        assert len(blocks_before) == 2
        assert blocks_before[0]["type"] == "h1"
        assert blocks_before[1]["type"] == "p"

        # Right click on the empty space directly below Heading 1
        h1 = await page.query_selector("h1")
        h1_box = await h1.bounding_box()
        click_y = h1_box["y"] + h1_box["height"] + 25
        click_x = h1_box["x"] + 50

        await page.mouse.click(click_x, click_y, button="right")
        await page.wait_for_selector("#context-menu", state="visible")

        # Add code block from menu
        add_code_btn = await page.query_selector('[data-action="add-code"]')
        await add_code_btn.click()

        blocks_after = await page.evaluate("""() => {
            return Array.from(document.getElementById('editor-page').children).map(c => ({
                tag: c.tagName,
                type: c.getAttribute('data-block-type')
            }));
        }""")

        # The new element must replace the empty space and be at index 1 directly below Heading 1!
        assert blocks_after[0]["type"] == "h1"
        assert blocks_after[1]["type"] == "code-block"

        await b.close()
