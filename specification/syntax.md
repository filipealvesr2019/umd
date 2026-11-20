# UMD 1.0 — Sintaxe

UMD (UI Markdown) é um formato de documento em texto puro, extensão `.umd`.
Todo `.umd` válido é também Markdown válido: se um ambiente não conhece um
componente, o conteúdo textual dentro dele continua legível.

## 1. Blocos Markdown

| Bloco         | Sintaxe                     |
| ------------- | --------------------------- |
| Título        | `# ` … `###### `            |
| Parágrafo     | linhas consecutivas         |
| Lista         | `- item`, `* item`, `1. item` |
| Citação       | `> texto`                   |
| Código        | ```` ``` ```` … ```` ``` ```` |
| Separador     | `---`                       |
| Comentário    | `<!-- … -->` (preservado)   |

## 2. Componentes

Um componente é um bloco delimitado por uma tag de abertura e uma de
fechamento:

```
[TABLE title="Vendas do mês"]
Produto | Quantidade | Valor
Notebook | 120 | R$ 12.000
[/TABLE]
```

Um componente vazio usa a forma auto-fechada:

```
[IMAGE src="foto.png" alt="Equipe" /]
```

Regras:

1. A tag abre no início da linha (espaço à esquerda é permitido).
2. A tag pode ter atributos: `chave="valor"`, `chave='valor'`, `chave=valor`
   ou apenas `chave` (booleano).
3. Componentes podem estar aninhados; cada abertura tem seu fechamento.
4. Nomes são insensíveis a caixa: `[card]` = `[CARD]`.
5. A linha da tag não contém mais nada além da tag.
6. Componentes são blocos; formatação inline usa Markdown (`**forte**`,
   `*ênfase*`, `` `código` ``, `[texto](url)`, `~~riscado~~`).

## 3. Componentes com corpo bruto

`TABLE` não interpreta Markdown no corpo: cada linha é uma linha da tabela,
as células são separadas por `|`.

```
[TABLE]
Produto | Quantidade | Valor
Notebook | 120 | R$ 12.000
Monitor | 85 | R$ 8.500
[/TABLE]
```

- A primeira linha é o cabeçalho.
- Uma segunda linha de alinhamento é opcional: `--- | ---: | ---` .
- Pipes no início/fim das linhas são opcionais.
- `\|` escapa um pipe literal dentro da célula.
- Todas as linhas devem ter o mesmo número de células que o cabeçalho.

## 4. Escapamento

| Sequência | Resultado          |
| --------- | ------------------ |
| `\[`      | `[` literal (início de linha) |
| `\\`      | `\` literal        |
| `\|`      | `|` literal (célula) |
| `\*`, `\_`, `` \` `` | caractere literal |

## 5. O que a versão 1.0 não tem

Documentado para não ser confundido com bug:

- Componentes inline (`texto [BADGE]novo[/BADGE]`). Use Markdown inline.
- Herança de estilo entre componentes.
- Expressões, condicionais, laços ou código executável. `.umd` é dado, não
  programa.
