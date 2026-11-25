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
7. **End-to-end (navegador)** — `tests/e2e/test_editor_e2e.py`. Abre `editor.html` em Chromium headless e percorre fluxos reais: roundtrip render/serialize, inserção de bloco, edição de texto, undo/redo, tema claro, gráficos, tabelas e imagens.
8. **Fuzzing / property-based** — `tests/test_fuzz.py` (Hypothesis). O parser não pode lançar exceção com entrada arbitrária; o texto-fonte é preservado e a contagem de parágrafos se mantém estável.
9. **Performance** — `tests/test_performance.py` (guardas) e `benchmarks/bench_parse.py` (baseline).

## Números atuais

- **100 testes** coletados, todos passando localmente (Python 3.14 / Windows).
- **Cobertura:** 76,07% (branch), limite 75%.
- **Baseline de parse** (Windows, Python 3.14) de `benchmarks/baseline.json`:

| Linhas | Caracteres | Parse (melhor) | Parse (média) | Render |
| ---: | ---: | ---: | ---: | ---: |
| 816 | 10.994 | 36,77 ms | 52,03 ms | 63,00 ms |
| 4.076 | 55.766 | 112,24 ms | 125,96 ms | 143,26 ms |
| 8.151 | 111.731 | 213,39 ms | 260,62 ms | 258,18 ms |
| 16.301 | 225.661 | 376,35 ms | 457,13 ms | 428,07 ms |

Atualize o baseline com `python benchmarks/bench_parse.py --save`.

## Integração contínua

- `.github/workflows/ci.yml` — Python 3.9/3.11/3.13: ruff + pytest com cobertura + upload Codecov.
- `.github/workflows/e2e.yml` — instala Chromium e roda `pytest tests/e2e -v`.
- `.github/workflows/mutation.yml` — `mutmut run` semanal/manual no Linux (mutmut não tem suporte nativo a Windows).

## Como rodar tudo localmente

```bash
pytest                                   # suíte completa (E2E é pulado se Playwright não estiver instalado)
pytest tests/e2e -v                      # suíte de navegador (requer: playwright install chromium)
pytest tests/test_fuzz.py -q             # testes property-based
pytest --cov --cov-report=term-missing   # limite de cobertura
python benchmarks/bench_parse.py         # tabela de performance
```

## Lacunas conhecidas

- O mutation testing está configurado, mas não roda em Windows nativo; use WSL ou o workflow de CI.
- A suíte E2E cobre os fluxos centrais do editor, não todos os controles interativos dos gráficos.
- As guardas de performance usam limites generosos, então pegam apenas regressões patológicas.

---

English version: [TEST_STRATEGY.md](TEST_STRATEGY.md)
