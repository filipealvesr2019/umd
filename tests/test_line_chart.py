import pytest
from playwright.sync_api import Page, sync_playwright
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

def test_line_chart_render_and_hover():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{str(EDITOR_HTML).replace('\\', '/')}")
        
        # Load sample document with line chart
        page.evaluate("(text) => renderDocument(text)", SAMPLE_LINE_UMD)
        
        # Verify chart wrapper exists
        chart = page.locator('.isolated-element[data-chart-type="line"]')
        assert chart.count() == 1
        assert chart.get_attribute("data-title") == "Training vs Validation Loss"
        
        # Verify legend has both series
        legends = page.locator('.line-legend-name')
        assert legends.count() == 2
        assert legends.nth(0).inner_text().strip() == "Train Loss"
        assert legends.nth(1).inner_text().strip() == "Val Loss"
        
        # Verify SVG contains polylines and points
        polylines = page.locator('.chart-polyline')
        assert polylines.count() == 2
        
        # 5 points * 2 series = 10 circle points
        points = page.locator('.chart-point')
        assert points.count() == 10
        
        # Verify tooltip on hover
        tooltip = page.locator('.chart-tooltip')
        assert tooltip.count() == 1
        
        # Hover first point
        points.first.hover()
        page.wait_for_timeout(100)
        
        # Check tooltip visible and contains series & value
        tip_text = tooltip.inner_text()
        assert "Train Loss" in tip_text
        assert "0.85" in tip_text
        
        # Verify table rows
        rows = page.locator('.line-data-table tbody tr')
        assert rows.count() == 5
        
        # Test serialization
        serialized = page.evaluate("() => serializeDocument()")
        assert '[CHART title="Training vs Validation Loss" type="line"]' in serialized
        assert 'Point | Train Loss | Val Loss' in serialized
        assert 'Epoch 1 | 0.85 | 0.92' in serialized
        assert 'Epoch 5 | 0.26 | 0.45' in serialized
        
        browser.close()

def test_line_chart_interactive_edit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file:///{str(EDITOR_HTML).replace('\\', '/')}")
        
        # Initialize empty document
        page.evaluate("() => renderDocument('')")
        
        # Open context menu and add line chart
        page.evaluate("""() => {
            const menu = document.getElementById('context-menu');
            const item = menu.querySelector('[data-action="add-chart-line"]');
            item.click();
        }""")
        
        # Verify chart was inserted
        chart = page.locator('.isolated-element[data-chart-type="line"]')
        assert chart.count() == 1
        
        # Add a point
        add_pt_btn = chart.locator('button:has-text("+ Add Point")')
        add_pt_btn.click()
        
        # Add a series
        add_series_btn = chart.locator('button:has-text("+ Add Line Series")')
        add_series_btn.click()
        
        # Series should now be 3
        legends = chart.locator('.line-legend-name')
        assert legends.count() == 3
        
        # Edit title
        title_input = chart.locator('.chart-title-input')
        title_input.fill("Custom Model Metrics")
        title_input.dispatch_event('input')
        
        # Check serialization has new title and 3 series
        serialized = page.evaluate("() => serializeDocument()")
        assert '[CHART title="Custom Model Metrics" type="line"]' in serialized
        assert 'Point | Train Loss | Val Loss | Series 3' in serialized
        
        # Test exportCleanClipboard
        clip_data = page.evaluate("""() => {
            const clean = exportCleanClipboard();
            return {
                html: clean.html,
                text: clean.text
            };
        }""")
        
        assert "Custom Model Metrics" in clip_data["html"]
        assert "<table" in clip_data["html"]
        assert "Point" in clip_data["html"]
        assert "Series 3" in clip_data["html"]
        assert "delete-series-btn" not in clip_data["html"]
        assert "chart-btn" not in clip_data["html"]
        
        browser.close()
