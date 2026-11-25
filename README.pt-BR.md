<div align="center">

# UI-Markdown (UMD)

**Documentos visuais interativos em texto puro**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Licença: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Testes](https://img.shields.io/badge/tests-100%20passed-brightgreen.svg)]()
[![CI](https://github.com/filipealvesr2019/umd/actions/workflows/ci.yml/badge.svg)](https://github.com/filipealvesr2019/umd/actions/workflows/ci.yml)
[![Cobertura](https://codecov.io/gh/filipealvesr2019/umd/branch/main/graph/badge.svg)](https://codecov.io/gh/filipealvesr2019/umd)
[![Zero Dependências](https://img.shields.io/badge/dependencies-0%20external-purple.svg)]()

*Combine a escrita fluida do Markdown com blocos de UI interativos, gráficos editáveis ao vivo, controles de tipografia rica e pipelines de arquitetura — armazenados em um único arquivo `.umd` de texto puro, sem arquivos companheiros.*

**English: [README.md](README.md)**

[Demo ao vivo](#-demo-ao-vivo) • [Visão geral](#-visão-geral) • [Recursos](#-recursos-principais) • [Início rápido](#-início-rápido) • [Referência de sintaxe](#-sintaxe--referência-de-componentes) • [API Python](#-api-python-e-report-builder) • [Licença](#-licença)

</div>

---

## 🌟 Visão geral

**UI-Markdown (`.umd`)** preenche a lacuna entre Markdown em texto puro e editores de documentos visuais ricos.

Ferramentas tradicionais forçam a escolha entre:
1. **Markdown puro**: leve e amigável ao Git, mas visualmente simples, com pouca interatividade.
2. **Apps proprietários**: visualmente ricos, mas presos em bancos de dados proprietários ou acompanhados de pacotes de múltiplos arquivos.

**UMD resolve isso.** Cada documento é armazenado inteiramente em **texto humano legível** com extensão `.umd`, com parser baseado em AST garantindo **preservação lossless de roundtrip (100%)**.

> 📖 **Novo no UMD?** Leia o guia completo passo a passo em **[docs/TUTORIAL.md](docs/TUTORIAL.md)**.

---

## ✨ Recursos principais

- **📄 Zero arquivos companheiros**: texto estilizado, métricas, gráficos, pipelines, callouts, checklists, imagens e tabelas vivem em um único arquivo `.umd` de texto puro.
- **🎨 Editor visual interativo**: editor WYSIWYG para Antigravity IDE e VS Code, com inserção de componentes por clique direito, Undo/Redo (`Ctrl+Z` / `Ctrl+Y`), scrollbars/botões hover-only e sincronização em tempo real.
- **🌗 Temas claro e escuro automáticos**: adapta-se a `vscode-dark`/`vscode-light` e `prefers-color-scheme`.
- **🖼️ Blocos de imagem nativos (`[IMAGE]` e `![alt](src)`)**: abra imagens locais, incorpore URLs diretas, edite legendas inline e redimensione com presets (S/M/L/Full), armazenando apenas caminhos em texto puro.
- **📝 Blocos de código e texto com auto-quebra**: syntax highlight (`python`, `json`, `html`, `js`, `sql`, `bash`) e quebra automática em blocos `text`.
- **🤖 Feito para agentes de IA e relatórios automatizados**:
  - `umd spec` e `umd install-skill`: referência de sintaxe compacta e instalador global de `SKILL.md` para Antigravity, Claude Code e Cursor.
  - `umd check --json` e `umd outline --json`: validação legível por máquina com dicas de correção.
  - Edições cirúrgicas via CLI: `umd add-row`, `umd set-metric`, `umd append-chart`.
  - Builder Python `Report` (`from umd.builder import Report`): API fluente sem dependências.
- **✍️ Toolbar universal de tipografia rica**: selecione qualquer texto para ajustar família, tamanho, espaçamento, cor e estilos inline (negrito, itálico, sublinhado, riscado, código).
- **🔄 Roundtrip lossless bidirecional**: edições visuais sincronizam de volta para `.umd` limpo sem reordenar blocos.
- **📊 Gráficos interativos embutidos**: comparison, curved, line, column, bar, pie/donut.
- **🧩 Blocos de layout e fluxo**: pipelines, cards, grids, progress, callouts, checklists, tabelas.
- **🛡️ Segurança em primeiro lugar**: defesa contra XSS, breakout de atributos, URLs inseguras (`javascript:`/`vbscript:`), fuzz handling resiliente.
- **⚡ Zero dependências externas**: core 100% biblioteca padrão do Python, parse <1ms.

---

## 🚀 Início rápido

### 1. Instalação

```bash
pip install ui-markdown
```

### 2. Instale a extensão do IDE

```bash
umd install
```

> **Dica:** recarregue o IDE (`Ctrl+Shift+P` → `Developer: Reload Window`). Clique em qualquer `.umd` para abrir no editor visual.

---

## 💻 Comandos CLI e kit para agentes de IA

```bash
umd install
umd install-skill
umd spec
umd check document.umd
umd check document.umd --json
umd outline document.umd --json
umd add-row report.umd --table 1 --values "Seed 133|HELD|88.0%" --write
umd set-metric report.umd --label "HELD" --value "7/8" --subtitle "87.5%" --write
umd append-chart report.umd --chart 1 --values "Exp 133|91.5" --write
umd render document.umd -o document.html
```

---

## 🧩 Sintaxe & referência de componentes

Veja **[docs/TUTORIAL.md](docs/TUTORIAL.md)** para o guia completo. Exemplos rápidos:

```markdown
[CHART title="Benchmark (%)" type="bar"]
GPT-4o | 88.5
Claude 3.5 Sonnet | 89.2
[/CHART]

[PIPELINE title="Pipeline de inferência"]
User Query -> Tokenizer -> Model -> Output
[/PIPELINE]

[COLUMNS gap="20"]
[CARD title="PARÂMETROS"]
70.6 Billion
[/CARD]
[/COLUMNS]

[PROGRESS label="Treinamento" value="94" max="100" /]
[CALLOUT tone="success" title="Verificado"]
Tudo passou.
[/CALLOUT]
```

---

## 🐍 API Python e Report Builder

```python
from umd import Report, styled, inline_code, parse, render_document, Document

report = (
    Report("Experimento 132 — Avaliação", "Resumo automatizado")
    .p(f"Status: {styled('PASS', color='#10b981', bold=True)} em {inline_code('HELD01')}")
    .cards([("TRAIN Exact", "18/20", "90.0%"), ("HELD Exact", "6/8", "75.0%")])
    .comparison_chart("Acurácia por regime (%)", [("TRAIN", [82.0, 90.0]), ("HELD", [62.5, 75.0])], series=["Exp 131", "Exp 132"])
    .table(["Seed", "Regime", "Score"], [["130", "HELD01", "84.6%"]])
    .callout("Zero erros de sintaxe garantidos.", tone="success", title="Verificado")
)
report.save("report_132.umd")

doc = Document(report.render())
assert doc.valid
html_output = render_document(doc)
```

---

## 🧪 Testes e verificação

```bash
pytest tests/
```

**Status:** 100 testes passando (unitários, roundtrip, segurança, edição, gráficos, CLI, end-to-end com Playwright, fuzzing com Hypothesis e guardas de performance). Cobertura: 76% (branch). Veja [docs/TEST_STRATEGY.pt-BR.md](docs/TEST_STRATEGY.pt-BR.md).

---

## 📄 Licença

Distribuído sob a **Licença MIT**. Veja [LICENSE](LICENSE).

---

> Documentação em inglês: [README.md](README.md)
