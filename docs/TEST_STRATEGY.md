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
7. **End-to-end (browser)** — `tests/e2e/test_editor_e2e.py`. Renders `editor.html` in headless Chromium and drives real editor flows: render/serialize roundtrip, block insertion, text editing, undo/redo, light theme, charts, tables and images.
8. **Fuzzing / property-based** — `tests/test_fuzz.py` (Hypothesis). The parser must never raise on arbitrary input; source text is preserved and paragraph counts stay stable.
9. **Performance** — `tests/test_performance.py` (guards) and `benchmarks/bench_parse.py` (baseline).

## Current numbers

- **100 tests** collected, all passing locally (Python 3.14 / Windows).
- **Coverage:** 76.07% (branch), threshold 75%.
- **Parse baseline** (Windows, Python 3.14) from `benchmarks/baseline.json`:

| Lines | Chars | Parse (best) | Parse (avg) | Render |
| ---: | ---: | ---: | ---: | ---: |
| 816 | 10,994 | 36.77 ms | 52.03 ms | 63.00 ms |
| 4,076 | 55,766 | 112.24 ms | 125.96 ms | 143.26 ms |
| 8,151 | 111,731 | 213.39 ms | 260.62 ms | 258.18 ms |
| 16,301 | 225,661 | 376.35 ms | 457.13 ms | 428.07 ms |

Refresh the baseline with `python benchmarks/bench_parse.py --save`.

## Continuous integration

- `.github/workflows/ci.yml` — Python 3.9/3.11/3.13: ruff + pytest with coverage + Codecov upload.
- `.github/workflows/e2e.yml` — installs Chromium and runs `pytest tests/e2e -v`.
- `.github/workflows/mutation.yml` — weekly/manual `mutmut run` on Linux (mutmut has no native Windows support).

## How to run everything locally

```bash
pytest                                   # full suite (E2E skips if Playwright is missing)
pytest tests/e2e -v                      # browser suite (needs: playwright install chromium)
pytest tests/test_fuzz.py -q             # property-based tests
pytest --cov --cov-report=term-missing   # coverage gate
python benchmarks/bench_parse.py         # performance table
```

## Known gaps

- Mutation testing is configured but cannot run on native Windows; use WSL or the CI workflow.
- The E2E suite covers the core editor flows, not every interactive chart control.
- Performance guards use generous thresholds, so they catch pathological regressions only.

---

Versão em português: [TEST_STRATEGY.pt-BR.md](TEST_STRATEGY.pt-BR.md)
