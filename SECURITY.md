# Security Policy

## Reporting a vulnerability

Report security issues privately to the maintainer instead of opening a public issue.

- Email: filipealvesrds2019@gmail.com
- Subject: `[SECURITY] ui-markdown: <short description>`

Include a description, impact, reproduction steps and affected versions.

You can expect an acknowledgement within 7 days and a fix or mitigation plan within 30 days for confirmed issues.

## Supported versions

Only the latest released version receives security fixes.

## Scope

The parser and HTML renderer include built-in protections against XSS, attribute breakout and unsafe URLs (`javascript:`/`vbscript:`). Security tests live in `tests/test_security.py`.

---

Versão em português: [SECURITY.pt-BR.md](SECURITY.pt-BR.md)
