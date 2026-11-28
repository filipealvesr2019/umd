"""Sync extension.js, editor.html, and LICENSE from the root UMD repo into vs_code_extension/."""
from __future__ import annotations

import shutil
from pathlib import Path

EXT_DIR = Path(__file__).resolve().parent
ROOT_DIR = EXT_DIR.parent


def sync() -> None:
    shutil.copyfile(ROOT_DIR / "extension_template.js", EXT_DIR / "extension.js")
    shutil.copyfile(ROOT_DIR / "editor.html", EXT_DIR / "editor.html")
    shutil.copyfile(ROOT_DIR / "LICENSE", EXT_DIR / "LICENSE")
    print("Synced extension.js, editor.html, and LICENSE into", EXT_DIR)


if __name__ == "__main__":
    sync()
