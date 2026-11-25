# Política de Segurança

## Reportando uma vulnerabilidade

Reporte problemas de segurança de forma privada ao mantenedor, em vez de abrir uma issue pública.

- E-mail: filipealvesrds2019@gmail.com
- Assunto: `[SECURITY] ui-markdown: <descrição curta>`

Inclua descrição, impacto, passos para reproduzir e versões afetadas.

Você receberá uma confirmação em até 7 dias e um plano de correção ou mitigação em até 30 dias para problemas confirmados.

## Versões suportadas

Apenas a última versão lançada recebe correções de segurança.

## Escopo

O parser e o renderer HTML incluem proteções contra XSS, breakout de atributos e URLs inseguras (`javascript:`/`vbscript:`). Testes de segurança ficam em `tests/test_security.py`.

---

English version: [SECURITY.md](SECURITY.md)
