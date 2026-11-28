"""Tests for Markdown (.md) compatibility layer and 'Open with UMD' extension integration."""
from __future__ import annotations

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from umd.installer import PACKAGE_JSON

EDITOR_HTML = ROOT / "editor.html"
EXTENSION_JS = ROOT / "extension_template.js"
EXEMPLOS_MD = ROOT / "examples" / "exemplos.md"


def test_extension_registers_open_with_umd_for_markdown():
    contributes = PACKAGE_JSON["contributes"]

    # Command "Open with UMD"
    commands = {c["command"]: c["title"] for c in contributes["commands"]}
    assert commands.get("umd.openWithUmd") == "Open with UMD"

    # Right-click menus in Explorer, Editor, and Tab Title for .md / .markdown
    menus = contributes["menus"]
    for menu_key in ("explorer/context", "editor/context", "editor/title/context"):
        entries = menus.get(menu_key, [])
        assert any(
            e["command"] == "umd.openWithUmd" and ".md" in e.get("when", "")
            for e in entries
        ), f"Missing umd.openWithUmd in {menu_key}"

    # Custom editors: .umd is default, .md/.markdown is option
    editors = {e["viewType"]: e for e in contributes["customEditors"]}
    assert editors["umd.editor"]["priority"] == "default"
    assert editors["umd.markdownEditor"]["priority"] == "option"
    md_patterns = {s["filenamePattern"] for s in editors["umd.markdownEditor"]["selector"]}
    assert "*.md" in md_patterns and "*.markdown" in md_patterns

    # extension_template.js wires up both providers and command
    ext_src = EXTENSION_JS.read_text(encoding="utf-8")
    assert "umd.markdownEditor" in ext_src
    assert "umd.openWithUmd" in ext_src
    assert "vscode.openWith" in ext_src


def test_open_full_markdown_examples_in_umd_editor():
    assert EXEMPLOS_MD.exists(), f"Missing {EXEMPLOS_MD}"
    md_text = EXEMPLOS_MD.read_text(encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1100, "height": 800})
        page_errors: list[str] = []
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        page.goto(f"file:///{str(EDITOR_HTML).replace(chr(92), '/')}")
        page.evaluate("(text) => renderDocument(text)", md_text)

        assert not page_errors, f"Uncaught JS errors rendering exemplos.md: {page_errors}"

        stats = page.evaluate("""() => {
            const root = document.getElementById('editor-page');
            const headings = Array.from(root.querySelectorAll('h1,h2,h3,h4')).map(h => h.innerText.trim());
            const links = Array.from(root.querySelectorAll('a.umd-md-link'));
            const refLink = links.find(a => a.textContent.includes('reference-style link'));
            const escapedP = Array.from(root.querySelectorAll('p')).find(p => p.textContent.includes('our-new-project'));
            return {
                headingCount: headings.length,
                hasAltH1: headings.includes('Alt-H1'),
                hasAltH2: headings.includes('Alt-H2'),
                strongCount: root.querySelectorAll('strong').length,
                emCount: root.querySelectorAll('em').length,
                delCount: root.querySelectorAll('del').length,
                ulCount: root.querySelectorAll('ul.notion-bullet-list').length,
                olCount: root.querySelectorAll('ol.notion-number-list').length,
                todoCount: root.querySelectorAll('.notion-todo-checkbox').length,
                linkCount: links.length,
                refLinkHref: refLink ? refLink.getAttribute('href') : '',
                imageBlockCount: root.querySelectorAll('.notion-image-block').length,
                codeBlockCount: root.querySelectorAll('.notion-code-block').length,
                tableCount: root.querySelectorAll('table.notion-table').length,
                quoteCount: root.querySelectorAll('blockquote.notion-quote').length,
                hrCount: root.querySelectorAll('hr.notion-hr').length,
                footnoteCount: root.querySelectorAll('.umd-footnote-ref').length,
                dlCount: root.querySelectorAll('.umd-md-html-block dl').length,
                escapedHasLiteralStars: escapedP ? escapedP.textContent.includes('*our-new-project*') : false,
                escapedHasNoEm: escapedP ? escapedP.querySelectorAll('em').length === 0 : false,
            };
        }""")

        assert stats["headingCount"] >= 18
        assert stats["hasAltH1"] is True
        assert stats["hasAltH2"] is True
        assert stats["strongCount"] >= 4
        assert stats["emCount"] >= 4
        assert stats["delCount"] >= 2
        assert stats["ulCount"] >= 2
        assert stats["olCount"] >= 2
        assert stats["todoCount"] >= 7
        assert stats["linkCount"] >= 6
        assert stats["refLinkHref"] == "https://www.mozilla.org"
        assert stats["imageBlockCount"] >= 5
        assert stats["codeBlockCount"] >= 10
        assert stats["tableCount"] >= 6
        assert stats["quoteCount"] >= 3
        assert stats["hrCount"] >= 10
        assert stats["footnoteCount"] >= 3
        assert stats["dlCount"] == 1
        assert stats["escapedHasLiteralStars"] is True
        assert stats["escapedHasNoEm"] is True

        # Also verify opening README.md and docs/TUTORIAL.md renders cleanly with zero JS errors
        for extra_md in (ROOT / "README.md", ROOT / "docs" / "TUTORIAL.md"):
            if extra_md.exists():
                page.evaluate("(text) => renderDocument(text)", extra_md.read_text(encoding="utf-8"))
                assert page.locator("#editor-page").inner_text().strip()
        assert not page_errors, f"Uncaught JS errors rendering repo .md files: {page_errors}"

        browser.close()
