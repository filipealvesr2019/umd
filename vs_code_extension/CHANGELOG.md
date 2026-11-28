# Changelog

## 0.0.9
- Added **Open with UMD** right-click menu for `.md` and `.markdown` files (Explorer, Editor, and Tab context menus) plus optional **UMD Visual Editor** in `Open With...`.
- Added full Markdown compatibility layer (Setext headings, ATX H1–H6, reference links/images, linked images, footnotes, escaped punctuation, nested blockquotes, `+`/`*`/`-` lists, `<dl>` blocks, and multi-table separation).
- Added `Ctrl+F` / `Cmd+F` in-document find & highlight using CSS Custom Highlight API.
- Fixed floating toolbar `<select>` dropdowns (`Font`, `Size`, `Spacing`) staying open cleanly.

## 0.0.8
- Fixed format toolbar selects closing prematurely on mouseup.

## 0.0.7
- Added native `[IMAGE]` & `![alt](src)` blocks with **Open Image** local file picker, direct URL support, editable captions, and hover width presets.
- Added automatic Light & Dark theme palettes (`vscode-light` / `vscode-dark`).
- Added full document Undo/Redo (`Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`).
- Added auto-wrapping for `text` blocks and hover-only scrollbars & action buttons.
- Fixed instant single-click insertion in the right-click component menu.
