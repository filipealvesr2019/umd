import pytest
from playwright.sync_api import sync_playwright
from pathlib import Path

EDITOR_HTML = Path(__file__).resolve().parent.parent / "editor.html"

SAMPLE_LINE_UMD = """# Line Chart Demo

[CHART title="Training vs Validation Loss" type="line"]
Point | Train Loss | Val Loss
Epoch 1 | 0.85 | 0.92
Epoch 2 | 0.62 | 0.71
Epoch 3 | 0.45 | 0.58
Epoch 4 | 0.34 | 0.49
Epoch 5 | 0.26 | 0.45
[/CHART]
"""

def test_direct_line_chart_no_table_and_interactions():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{str(EDITOR_HTML).replace('\\', '/')}")
        
        # Load sample document
        page.evaluate("(text) => renderDocument(text)", SAMPLE_LINE_UMD)
        
        # 1. Verify NO TABLE exists
        assert page.locator('.line-data-table').count() == 0
        assert page.locator('.line-data-table-wrap').count() == 0
        
        # 2. Verify large SVG canvas
        svg = page.locator('.line-chart-svg')
        assert svg.count() == 1
        viewbox = svg.get_attribute("viewBox")
        assert "900 380" in viewbox
        
        # 3. Verify points and series count
        polylines = page.locator('.chart-polyline')
        assert polylines.count() == 2
        
        points = page.locator('.chart-point')
        assert points.count() == 10
        
        # 4. Click a point to open popover
        first_point = points.first
        first_point.click()
        
        popover = page.locator('.chart-point-popover')
        assert popover.count() == 1
        
        # Edit point value in popover
        val_input = popover.locator('.popover-input')
        val_input.fill("0.99")
        popover.locator('.popover-btn-save').click()
        
        # Verify popover closed
        assert not popover.is_visible()
        
        # Verify serialization reflects new value
        serialized = page.evaluate("() => serializeDocument()")
        assert "Epoch 1 | 0.99 | 0.92" in serialized
        
        # 5. Delete a point via popover
        last_point = page.locator('.chart-point').last
        last_point.click()
        assert popover.is_visible()
        popover.locator('.popover-btn-del').click()
        
        # Point count should decrease from 10 to 8
        assert page.locator('.chart-point').count() == 8
        
        # 6. Click canvas to add a new line series
        # Click in the middle of SVG plot area (e.g. x=400, y=200)
        svg_box = svg.bounding_box()
        page.mouse.click(svg_box["x"] + 400, svg_box["y"] + 200)
        
        # Polylines should now be 3
        assert page.locator('.chart-polyline').count() == 3
        assert page.locator('.line-legend-name').count() == 3
        
        # 7. Test clean clipboard export
        clip_data = page.evaluate("""() => {
            const clean = exportCleanClipboard();
            return {
                html: clean.html,
                text: clean.text
            };
        }""")
        
        assert "Training vs Validation Loss" in clip_data["html"]
        assert "<table" in clip_data["html"]
        assert "delete" not in clip_data["html"].lower()
        
        # 8. Test clicking on a line hitarea to add a point
        # Get first hitarea
        hitarea = page.locator('.chart-line-hitarea').first
        box = hitarea.bounding_box()
        # Click on line
        page.mouse.click(box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.5)
        
        # Point count should increase
        new_point_count = page.locator('.chart-point').count()
        assert new_point_count > 8
        
        # 9. Test clicking X-axis label to edit text
        first_x_label = page.locator('.editable-x-label').first
        assert first_x_label.count() == 1
        first_x_label.click()
        
        inline_input = page.locator('.axis-x-inline-input')
        assert inline_input.count() == 1
        inline_input.fill("Epoch Alpha")
        inline_input.press("Enter")
        
        # Verify text updated on SVG
        assert page.locator('.editable-x-label').first.text_content() == "Epoch Alpha"
        
        # Verify serialization has new label
        ser = page.evaluate("() => serializeDocument()")
        assert "Epoch Alpha" in ser
        
        browser.close()
