# UMD 1.0 — Gramática

Gramática em EBNF do formato `.umd`. Implementação de referência em
`umd/core/lexer.py` e `umd/core/parser.py`.

```ebnf
document      = { block } ;

block         = blank | comment | markdown_block | component ;

blank         = { " " | "\t" }, newline ;

comment       = "<!--", { any - "-->" }, "-->" ;

(* ---------- componentes ---------- *)

component     = open_tag, { block }, close_tag
              | self_tag ;

open_tag      = ws, "[", name, { attr }, ws, "]", ws, newline ;
close_tag     = ws, "[", "/", name, ws, "]", ws, newline ;
self_tag      = ws, "[", name, { attr }, ws, "/", ws, "]", ws, newline ;

name          = letter, { letter | digit | "_" | "-" } ;

attr          = ws, attr_name, [ ws, "=", ws, attr_value ] ;
attr_name     = letter | "_", { letter | digit | "_" | "-" } ;
attr_value    = quoted | bare ;
quoted        = '"', { any - '"' }, '"'
              | "'", { any - "'" }, "'" ;
bare          = { any - ws - "]" - "/" } ;

(* ---------- markdown ---------- *)

markdown_block = heading | fenced_code | hr | list | quote | paragraph ;

heading       = ( "#", 1*6 "#" ), 1*( " " | "\t" ), text, newline ;
fenced_code   = fence_open, { any }, fence_close ;
fence_open    = ws, ( "```" | "~~~" ), { any }, newline ;
fence_close   = ws, ( "```" | "~~~" ), ws, newline ;
hr            = ws, ( 3*"-" | 3*"*" | 3*"_" ), ws, newline ;
list          = list_item, { list_item } ;
list_item     = ws, ( "-" | "*" | "+" | 1*digit "." ), 1*( " " | "\t" ), text, newline ;
quote         = quote_line, { quote_line } ;
quote_line    = ws, ">", [ " " ], text, newline ;
paragraph     = text_line, { text_line } ;
text_line     = ws, { any - newline }, newline ;

(* ---------- inline ---------- *)

inline        = text | strong | emphasis | code | link | strike ;
strong        = "**", 1*any, "**" | "__", 1*any, "__" ;
emphasis      = "*", 1*any, "*" | "_", 1*any, "_" ;
code          = "`", 1*any, "`" ;
link          = "[", 1*any, "]", "(", 1*any, ")" ;
strike        = "~~", 1*any, "~~" ;
```

## Eventos léxicos

O lexer produz um token por linha (ou por tag, ou por comentário):

| Token             | Origem                                  |
| ----------------- | --------------------------------------- |
| `MD_LINE`         | linha de conteúdo Markdown              |
| `BLANK`           | linha vazia                             |
| `COMPONENT_OPEN`  | `[NOME ...]` no início da linha         |
| `COMPONENT_CLOSE` | `[/NOME]`                               |
| `COMPONENT_SELF`  | `[NOME ... /]`                          |
| `COMMENT`         | `<!-- … -->` (pode ocupar várias linhas)|
| `EOF`             | fim do texto                            |

Cada token carrega `start` e `end` (deslocamentos no texto normalizado) e
`line`/`column`. É essa informação que torna o *source mapping* possível: toda
edição visual vira a substituição de um intervalo exato do arquivo original.
