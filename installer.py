"""Installer for UI-Markdown Visual Editor extension (VS Code & Antigravity IDE).

Deploys the extension locally to ~/.antigravity-ide/extensions/umd-editor and ~/.vscode/extensions/umd-editor,
rendering .umd documents as clean, Notion-style interactive pages.
"""
from __future__ import annotations

import json
from pathlib import Path

EXTENSION_NAME = "umd-editor"

PACKAGE_JSON = {
    "name": "ui-markdown-editor",
    "displayName": "UI-Markdown Visual Editor",
    "description": "Interactive Notion-style visual editor for .umd files",
    "version": "0.0.9",
    "publisher": "ui-markdown",
    "engines": {
        "vscode": "^1.60.0"
    },
    "categories": ["Other"],
    "activationEvents": [
        "onCustomEditor:umd.editor",
        "onCustomEditor:umd.markdownEditor",
        "onCommand:umd.openWithUmd"
    ],
    "main": "./extension.js",
    "contributes": {
        "commands": [
            {
                "command": "umd.openWithUmd",
                "title": "Open with UMD"
            }
        ],
        "menus": {
            "explorer/context": [
                {
                    "command": "umd.openWithUmd",
                    "when": "resourceExtname == .md || resourceExtname == .markdown",
                    "group": "navigation@1"
                }
            ],
            "editor/context": [
                {
                    "command": "umd.openWithUmd",
                    "when": "editorLangId == markdown || resourceExtname == .md || resourceExtname == .markdown",
                    "group": "navigation@1"
                }
            ],
            "editor/title/context": [
                {
                    "command": "umd.openWithUmd",
                    "when": "editorLangId == markdown || resourceExtname == .md || resourceExtname == .markdown",
                    "group": "navigation@1"
                }
            ]
        },
        "customEditors": [
            {
                "viewType": "umd.editor",
                "displayName": "UI-Markdown Visual Editor",
                "selector": [
                    {
                        "filenamePattern": "*.umd"
                    }
                ],
                "priority": "default"
            },
            {
                "viewType": "umd.markdownEditor",
                "displayName": "UMD Visual Editor",
                "selector": [
                    {
                        "filenamePattern": "*.md"
                    },
                    {
                        "filenamePattern": "*.markdown"
                    }
                ],
                "priority": "option"
            }
        ]
    }
}


def get_target_directories() -> list[Path]:
    """Returns extension folders for VS Code and Antigravity IDE."""
    home = Path.home()
    return [
        home / ".antigravity-ide" / "extensions",
        home / ".vscode" / "extensions",
    ]


def install_extension() -> list[Path]:
    """Installs the extension locally."""
    current_dir = Path(__file__).resolve().parent
    template_js = (current_dir / "extension_template.js").read_text(encoding="utf-8")
    editor_html = (current_dir / "editor.html").read_text(encoding="utf-8")

    installed_paths = []
    for base in get_target_directories():
        ext_dir = base / EXTENSION_NAME
        ext_dir.mkdir(parents=True, exist_ok=True)

        package_path = ext_dir / "package.json"
        package_path.write_text(json.dumps(PACKAGE_JSON, indent=2), encoding="utf-8")

        ext_path = ext_dir / "extension.js"
        ext_path.write_text(template_js, encoding="utf-8")

        html_path = ext_dir / "editor.html"
        html_path.write_text(editor_html, encoding="utf-8")

        installed_paths.append(ext_dir)
    return installed_paths


def uninstall_extension() -> list[Path]:
    """Removes the extension."""
    import shutil
    removed = []
    for base in get_target_directories():
        ext_dir = base / EXTENSION_NAME
        if ext_dir.exists():
            shutil.rmtree(ext_dir, ignore_errors=True)
            removed.append(ext_dir)
    return removed
