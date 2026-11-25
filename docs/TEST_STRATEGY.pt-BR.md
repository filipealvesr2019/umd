# Estratégia de Testes — UI-Markdown

## Escopo

UI-Markdown (UMD) é um parser, renderer, CLI e editor para documentos `.umd`. Objetivos de qualidade: roundtrip lossless, segurança contra XSS, AST estável e CLI confiável.

## Camadas de teste

1. **Testes unitários** — `tests/test_parser.py`, `tests/test_render.py`, `tests/test_add_position.py`.
   Gramática do parser, tokens, diagnósticos e validação.
2. **Roundtrip** — `tests/test_roundtrip.py`. Igualdade parse → render → parse.
3. **Segurança** — `tests/test_security.py`. XSS, breakout de atributos e URLs inseguras.
4. **Edição/UX** — `tests/test_editing.py`, `tests/test_undo_and_text_wrap.py`, `tests/test_source_map.py`. Source maps, undo/redo, quebra de texto.
5. **Gráficos e clipboard** — `tests/test_line_chart.py`, `tests/test_clipboard_visuals.py`.
6. **CLI e agent kit** — `tests/test_agent_kit.py`. `umd check`, `umd outline`, edições cirúrgicas.

## Cobertura

Aproximadamente 76% (branch) / 86% (statement). O mínimo é 75%, garantido pelo `--cov` e `fail_under` no `pyproject.toml`.

Execute com:

```bash
pytest --cov --cov-report=term-missing
```

## Integração contínua

O GitHub Actions roda a suíte em Python 3.9, 3.11 e 3.13, executa lint com ruff e envia a cobertura ao Codecov.

## Lacunas planejadas

- Testes end-to-end com Playwright para o editor visual.
- Fuzzing e testes property-based do parser.
- Benchmarks de performance para documentos grandes.
- Mutation testing.

---

English version: [TEST_STRATEGY.md](TEST_STRATEGY.md)
