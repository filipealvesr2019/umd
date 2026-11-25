# Contribuindo com o UI-Markdown

## Configuração de desenvolvimento

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## Executando os testes

```bash
pytest
pytest --cov --cov-report=term-missing
```

## Lint

```bash
ruff check .
ruff format --check .
```

## Mensagens de commit

Use commits descritivos e convencionais (`feat:`, `fix:`, `test:`, `docs:`). Evite mensagens genéricas como "add".

## Pull requests

- Adicione ou atualize testes para qualquer mudança de comportamento.
- Mantenha a cobertura em 75% ou mais.
- Atualize badges/contagens no README quando o total de testes mudar.

---

English version: [CONTRIBUTING.md](CONTRIBUTING.md)
