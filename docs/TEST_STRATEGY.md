# Test Strategy — UI-Markdown

## Scope

UI-Markdown (UMD) is a parser, renderer, CLI and editor for `.umd` documents. Quality goals: lossless roundtrip, XSS safety, stable AST and a reliable CLI.

## Test layers

1. **Unit tests** — `tests/test_parser.py`, `tests/test_render.py`, `tests/test_add_position.py`.
   Parser grammar, tokens, diagnostics and validation.
2. **Roundtrip** — `tests/test_roundtrip.py`. Parse → render → parse equality.
3. **Security** — `tests/test_security.py`. XSS, attribute breakout and unsafe URLs.
4. **Editing/UX** — `tests/test_editing.py`, `tests/test_undo_and_text_wrap.py`, `tests/test_source_map.py`. Source maps, undo/redo, text wrapping.
5. **Charts and clipboard** — `tests/test_line_chart.py`, `tests/test_clipboard_visuals.py`.
6. **CLI and agent kit** — `tests/test_agent_kit.py`. `umd check`, `umd outline`, surgical edits.

## Coverage

Approximately 76% (branch) / 86% (statement). The minimum is 75%, enforced by `--cov` and `fail_under` in `pyproject.toml`.

Run it with:

```bash
pytest --cov --cov-report=term-missing
```

## Continuous integration

GitHub Actions runs the suite on Python 3.9, 3.11 and 3.13, lints with ruff and uploads coverage to Codecov.

## Planned gaps

- Playwright end-to-end tests for the visual editor.
- Parser fuzzing and property-based tests.
- Performance benchmarks for large documents.
- Mutation testing.

---

Versão em português: [TEST_STRATEGY.pt-BR.md](TEST_STRATEGY.pt-BR.md)
