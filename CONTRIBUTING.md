# Contributing to UI-Markdown

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Running the tests

```bash
pytest
pytest --cov --cov-report=term-missing
```

## Linting

```bash
ruff check .
ruff format --check .
```

## Commit messages

Use descriptive, conventional commits (`feat:`, `fix:`, `test:`, `docs:`). Avoid generic messages such as "add".

## Pull requests

- Add or update tests for any behavior change.
- Keep coverage at or above 75%.
- Update README badges/counts when the test total changes.

---

Versão em português: [CONTRIBUTING.pt-BR.md](CONTRIBUTING.pt-BR.md)
