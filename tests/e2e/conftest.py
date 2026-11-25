"""Shared Playwright fixtures for editor end-to-end tests."""

from pathlib import Path

import pytest

playwright_api = pytest.importorskip(
    "playwright.sync_api",
    reason="playwright is required for the end-to-end suite",
)

EDITOR_HTML = Path(__file__).resolve().parents[2] / "editor.html"


def editor_url() -> str:
    """Return a file:// URL that works on Windows and POSIX."""
    return "file:///" + str(EDITOR_HTML).replace("\\", "/")


@pytest.fixture(scope="module")
def page():
    """Fresh browser per test module, fully torn down before other suites run."""
    with playwright_api.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        page.goto(editor_url())
        page.wait_for_selector("#editor-page")
        yield page
        context.close()
        browser.close()
