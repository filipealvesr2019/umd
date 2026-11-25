# Changelog

## [0.0.9] — não lançado

### Testes
- 100 testes, todos passando localmente: parser, renderização, roundtrip, segurança, edição, gráficos, CLI, E2E de navegador, fuzzing e guardas de performance.
- Cobertura 76,07% (branch), limite >= 75%.
- Adicionada suíte Playwright em `tests/e2e/` para o `editor.html` (render/serialize, inserção de bloco, edição, undo/redo, tema, gráficos, tabelas e imagens).
- Adicionado `tests/test_fuzz.py` com Hypothesis (o parser nunca lança exceção com entrada arbitrária e o texto-fonte é preservado).
- Adicionados `tests/test_performance.py` e `benchmarks/bench_parse.py` com baseline registrado (`benchmarks/baseline.json`).

### Qualidade
- Adicionado workflow de CI com matriz Python e upload de cobertura.
- Adicionado workflow dedicado de E2E (instala Chromium + `pytest tests/e2e`).
- Adicionado workflow semanal/manual de mutation testing (mutmut no Linux).
- Adicionada configuração ruff e hooks de pre-commit.
- Adicionada documentação de estratégia de testes, contribuição, segurança e changelog (versões em inglês + pt-BR).
- Adicionado README.pt-BR.md como versão separada em português.

---

English version: [CHANGELOG.md](CHANGELOG.md)
