# Changelog

## [0.0.9] — unreleased

### Tests
- 100 tests, all passing locally: parser, rendering, roundtrip, security, editing, charts, CLI, browser E2E, fuzzing and performance guards.
- Coverage 76.07% (branch), threshold >= 75%.
- Added `tests/e2e/` Playwright suite for `editor.html` (render/serialize, block insertion, editing, undo/redo, theme, charts, tables, images).
- Added `tests/test_fuzz.py` with Hypothesis (parser never raises on arbitrary input, source text preserved).
- Added `tests/test_performance.py` and `benchmarks/bench_parse.py` with a recorded baseline (`benchmarks/baseline.json`).

### Quality
- Added CI workflow with Python matrix and coverage upload.
- Added dedicated E2E workflow (Chromium install + `pytest tests/e2e`).
- Added scheduled/manual mutation testing workflow (mutmut on Linux).
- Added ruff configuration and pre-commit hooks.
- Added test strategy, contribution, security and changelog documentation (English + pt-BR versions).
- Added README.pt-BR.md as a separate Portuguese version.

---

Versão em português: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)
