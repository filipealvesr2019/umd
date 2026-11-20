# Guia Oficial de Publicação e Documentação — UI-Markdown (`ui-markdown`)

Este documento é o seu manual passo a passo para:
1. Publicar a biblioteca no **PyPI** (Python Package Index oficial).
2. Criar e documentar o repositório no **GitHub** com o padrão dos projetos Python mais prestigiados.
3. Documentar o código internamente no **Python** (docstrings, MkDocs e GitHub Pages).

---

## 1. Identidade e Nomes do Pacote

| Item | Nome Recomendado | Justificativa |
| :--- | :--- | :--- |
| **Nome no PyPI** | `ui-markdown` | Nome moderno, claro e sem conflito de namespace. |
| **Comando de Instalação** | `pip install ui-markdown` | Padrão mundial de instalação Python. |
| **Comandos no Terminal (CLI)** | `umd` e `uimd` | Atalhos rápidos definidos em `[project.scripts]`. |
| **Import no Código Python** | `import umd` | Sintaxe concisa: `from umd import Document, render_document`. |
| **Repositório GitHub** | `filipealvesr2019/ui-markdown` | Padrão limpo e profissional. |

---

## 2. Preparação dos Arquivos do Projeto

Certifique-se de que a raiz do seu projeto possui esta estrutura:

```text
ui-markdown/
├── umd/                     # Código-fonte Python
│   ├── core/                # Lexer, Parser, AST
│   ├── document/            # Document Model, Source Mapping, Patches
│   ├── renderers/           # Renderizador HTML
│   ├── cli.py               # Interface de linha de comando (CLI)
│   ├── installer.py         # Instalador da extensão VS Code / Antigravity
│   ├── editor.html          # Editor visual estilo Notion
│   └── extension_template.js
├── examples/                # Exemplos oficiais em inglês (.umd)
│   ├── product_spec.umd
│   ├── sales_report.umd
│   ├── project_roadmap.umd
│   └── quarterly_budget.umd
├── tests/                   # 61 testes automatizados (pytest)
├── pyproject.toml           # Metadados oficiais de empacotamento
├── README.md                # Documentação da página inicial do GitHub
├── LICENSE                  # Licença MIT
└── PUBLISHING_GUIDE.md      # Este guia
```

---

## 3. Como Gerar o Pacote Python (Build)

### Passo 3.1: Instalar as ferramentas oficiais do PyPA
No seu terminal (PowerShell ou Bash):
```bash
python -m pip install --upgrade pip build twine
```

### Passo 3.2: Gerar os binários do pacote (Wheel e Source Distribution)
Na pasta do projeto (`G:\codeworld\umd`):
```bash
python -m build
```
Isso criará uma pasta `dist/` com dois arquivos:
- `ui_markdown-1.0.0-py3-none-any.whl` (binário pré-compilado de instalação instantânea)
- `ui_markdown-1.0.0.tar.gz` (código-fonte completo)

### Passo 3.3: Verificar a integridade dos pacotes
```bash
python -m twine check dist/*
```
*Saída esperada:* `PASSED` para ambos os arquivos.

---

## 4. Como Publicar no PyPI Oficial

### Passo 4.1: Criar conta no PyPI
1. Acesse [pypi.org/account/register](https://pypi.org/account/register/) e crie sua conta gratuita.
2. Em **Account settings** > **API tokens**, clique em **Add API token**.
3. Nomeie o token (ex: `ui-markdown-upload`) e copie o token secreto que começa com `pypi-...`.

### Passo 4.2: Enviar para o PyPI (1 comando)
No terminal:
```bash
python -m twine upload dist/*
```
- **Username:** `__token__`
- **Password:** cole o seu token `pypi-...`

Pronto! Seu pacote estará imediatamente ativo mundialmente no endereço:
`https://pypi.org/project/ui-markdown/`

Qualquer pessoa no planeta agora poderá instalar com:
```bash
pip install ui-markdown
umd install
```

---

## 5. Como Documentar o Pacote no GitHub

Um repositório GitHub de alto impacto possui 5 elementos essenciais:

### 5.1 Badges de Status no Topo do README
Adicione estes badges no topo do seu `README.md`:
```markdown
# UI-Markdown (`.umd`)

[![PyPI version](https://img.shields.io/pypi/v/ui-markdown.svg?color=blue)](https://pypi.org/project/ui-markdown/)
[![Python versions](https://img.shields.io/pypi/pyversions/ui-markdown.svg)](https://pypi.org/project/ui-markdown/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-61%20passed-success.svg)]()
[![Pure Python](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()
```

### 5.2 Estrutura Recomendada do README.md
1. **Pitch em 1 frase:** O que a biblioteca faz de único (ex: *"Notion fluidity meets Markdown purity — interactive visual documents stored in 100% plain text with zero companion files"*).
2. **Key Features:**
   - Visual Notion-style editing inside VS Code & Antigravity IDE.
   - Pure plain text `.umd` storage (zero database lock-in, zero companion `.html` files).
   - AST-backed lossless bidirectional sync.
   - Built-in rich UI blocks: Interactive Tables with dynamic rows/columns, Stat Cards, Callouts, Task Checklists, and Toggles.
3. **Instalação Rápida (Quickstart):**
   ```bash
   pip install ui-markdown
   umd install
   ```
4. **Exemplo de Uso via Python API:**
   ```python
   from umd import Document, render_document

   doc = Document(open("report.umd").read())
   table = doc.tables()[0]
   doc.set_cell(table.id, row=1, col=2, value="$120,000")
   doc.save()
   ```
5. **CLI Cheat Sheet:**
   - `umd install` — instala a extensão visual no VS Code/Antigravity.
   - `umd check document.umd` — valida sintaxe e spans.
   - `umd outline document.umd` — lista blocos e componentes.
   - `umd html document.umd -o output.html` — exporta para HTML estático.

---

## 6. Como Documentar o Código Internamente no Python

### 6.1 Docstrings Padrão Google no Código
Toda classe e método público deve seguir a convenção de docstrings:

```python
def render_document(source: str | Document, standalone: bool = True) -> str:
    """Renders a UMD document into clean, responsive HTML.

    Args:
        source: Plain text string or Document instance.
        standalone: If True, wraps output in a full HTML page with embedded CSS.

    Returns:
        Rendered HTML markup string.

    Example:
        >>> html = render_document("# Title\\n\\nHello world!")
        >>> "<h1>Title</h1>" in html
        True
    """
```

### 6.2 Gerador de Site de Documentação Automático (MkDocs)
Para gerar uma documentação web linda no GitHub Pages:

1. Instale o MkDocs Material:
   ```bash
   pip install mkdocs-material mkdocstrings[python]
   ```
2. Crie o arquivo `mkdocs.yml`:
   ```yaml
   site_name: UI-Markdown
   site_description: Interactive Notion-style visual documents in pure plain text
   site_url: https://filipealvesr2019.github.io/ui-markdown/
   theme:
     name: material
     palette:
       scheme: slate
       primary: blue
       accent: indigo
     features:
       - navigation.instant
       - content.code.copy
   plugins:
     - search
     - mkdocstrings
   ```
3. Publique a documentação no GitHub Pages com um único comando:
   ```bash
   mkdocs gh-deploy
   ```

---

## 7. Automação CI/CD com GitHub Actions

Crie o arquivo `.github/workflows/ci.yml` para rodar os testes a cada `git push`:

```yaml
name: CI & Publish

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest hypothesis
        pip install -e .
    - name: Run test suite
      run: |
        pytest tests/

  publish:
    needs: test
    if: github.event_name == 'release'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - name: Build and Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install build twine
        python -m build
        twine upload dist/*
```

---

## Resumo dos Comandos Rápidos

| Objetivo | Comando |
| :--- | :--- |
| **Instalar ferramentas** | `pip install build twine` |
| **Gerar pacote** | `python -m build` |
| **Validar pacote** | `twine check dist/*` |
| **Publicar no PyPI** | `twine upload dist/*` |
| **Instalar o pacote publicado** | `pip install ui-markdown && umd install` |
