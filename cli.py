"""Linha de comando do UMD (sem dependências externas).

    python -m umd check    relatorio.umd
    python -m umd outline  relatorio.umd
    python -m umd ast      relatorio.umd
    python -m umd grid     relatorio.umd table#1
    python -m umd set-cell relatorio.umd table#1 1 2 "R$ 13.000" --write
    python -m umd append-row relatorio.umd table#1 --value "Mouse" --value 40 --value "R$ 3.200"
    python -m umd demo
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from .agent_kit import (
    UMD_SPEC,
    add_table_row,
    append_chart_row,
    build_outline,
    diagnostic_hint,
    install_skill,
    set_metric,
)
from .document.model import Document
from .document.persistence import open_document
from .installer import install_extension, uninstall_extension
from .renderers.html import render_document

EXAMPLES = Path(__file__).resolve().parent / "examples"


def _print_diagnostics(document: Document) -> int:
    if not document.diagnostics:
        print("sem problemas")
        return 0
    for diagnostic in document.diagnostics:
        print(diagnostic)
    return 1 if document.errors() else 0


def cmd_check(args) -> int:
    document = open_document(args.file)
    if getattr(args, "json", False):
        payload = {
            "file": str(document.path),
            "valid": document.valid,
            "error_count": len(document.errors()),
            "warning_count": len(document.warnings()),
            "diagnostics": [
                {
                    **d.to_dict(),
                    "hint": diagnostic_hint(d.code),
                }
                for d in document.diagnostics
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1 if document.errors() else 0

    status = _print_diagnostics(document)
    print(
        f"{len(document.nodes())} nós, {len(document.tables())} tabela(s), "
        f"{len(document.errors())} erro(s), {len(document.warnings())} aviso(s)"
    )
    return status


def cmd_outline(args) -> int:
    if getattr(args, "json", False):
        payload = build_outline(args.file)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0 if payload["valid"] else 1

    payload = build_outline(args.file)
    for item in payload["items"]:
        kind = item["kind"].upper()
        line = f"L{item['line']}"
        idx = f"#{item['index']}" if "index" in item else ""
        label = item.get("title") or item.get("label") or item.get("lang") or ""
        extra = ""
        if item["kind"] == "table" and "headers" in item:
            extra = f" ({item.get('rows', 0)} linhas: {', '.join(item['headers'])})"
        elif item["kind"] == "chart":
            extra = f" [type={item.get('chart_type', 'bar')}]"
        elif item["kind"] == "card" and "value" in item:
            extra = f" = {item['value']}"
        elif item["kind"] == "progress":
            extra = f" = {item.get('value')}/{item.get('max')}"
        print(f"{line:<6} {kind + idx:<12} {label}{extra}")
    return 0 if payload["valid"] else 1


def cmd_spec(args) -> int:
    print(UMD_SPEC.strip())
    return 0


def cmd_install_skill(args) -> int:
    paths = install_skill(getattr(args, "dir", None))
    print("UMD Agent Skill instalada com sucesso:")
    for p in paths:
        print(f"  -> {p}")
    return 0


def cmd_add_row(args) -> int:
    raw_vals = args.value or ([args.values] if args.values else [])
    ok, msg, _ = add_table_row(args.file, args.table, raw_vals, write=args.write)
    print(msg)
    if not ok:
        return 2
    if args.write:
        print(f"gravado: {args.file}")
    else:
        print("(dry-run; use --write para gravar)")
    return 0


def cmd_set_metric(args) -> int:
    ok, msg, _ = set_metric(
        args.file,
        args.label,
        args.value,
        subtitle=args.subtitle,
        write=args.write,
    )
    print(msg)
    if not ok:
        return 2
    if args.write:
        print(f"gravado: {args.file}")
    else:
        print("(dry-run; use --write para gravar)")
    return 0


def cmd_append_chart(args) -> int:
    raw_vals = args.value or ([args.values] if args.values else [])
    ok, msg, _ = append_chart_row(args.file, args.chart, raw_vals, write=args.write)
    print(msg)
    if not ok:
        return 2
    if args.write:
        print(f"gravado: {args.file}")
    else:
        print("(dry-run; use --write para gravar)")
    return 0


def cmd_ast(args) -> int:
    document = open_document(args.file)
    payload = {
        "version": "1.0",
        "file": str(document.path),
        "valid": document.valid,
        "root": document.root.to_dict(),
        "diagnostics": [d.to_dict() for d in document.diagnostics],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_grid(args) -> int:
    document = open_document(args.file)
    for row in document.grid(args.table):
        print(" | ".join(cell.ljust(12) for cell in row).rstrip())
    return 0


def cmd_set_cell(args) -> int:
    document = open_document(args.file)
    result = document.set_cell(args.table, args.row, args.col, args.value)
    print(result.message)
    if not result.ok:
        return 2
    if args.write:
        document.save()
        print(f"gravado: {document.path}")
    else:
        print("(dry-run; use --write para gravar)")
    return 0


def cmd_append_row(args) -> int:
    document = open_document(args.file)
    result = document.append_row(args.table, args.value)
    print(result.message)
    if not result.ok:
        return 2
    if args.write:
        document.save()
        print(f"gravado: {document.path}")
    else:
        print("(dry-run; use --write para gravar)")
    return 0


def cmd_render(args) -> int:
    document = open_document(args.file)
    output = Path(args.out) if args.out else document.path.with_suffix(".html")
    output.write_text(render_document(document), encoding="utf-8")
    print(f"gerado: {output}")
    if document.diagnostics:
        _print_diagnostics(document)
    return 0


def cmd_demo(args) -> int:
    """Executa o ciclo do MVP: abrir, ler, editar célula, salvar, reabrir."""
    source = Path(args.file) if args.file else EXAMPLES / "relatorio.umd"
    workdir = Path(tempfile.mkdtemp(prefix="umd_demo_"))
    target = workdir / source.name
    shutil.copyfile(source, target)

    print("1. interpretar o arquivo")
    document = open_document(target)
    print(f"   {target}  ->  {len(document.nodes())} nós, válido={document.valid}")

    print("2. localizar título, parágrafo e tabela")
    table = document.tables()[0]
    print(f"   título: {document.root.children[0].text!r}")
    print(f"   tabela: {table.id} na linha {table.line}")
    for row in document.grid(table.id):
        print("   " + " | ".join(row))

    print("3. selecionar uma célula")
    cell = document.source_map.cell(table.id, 1, 2)
    print(f"   {cell.id} = {cell.text!r}  span={[cell.start, cell.end]}")

    print("4. modificar o conteúdo")
    result = document.set_cell(table.id, 1, 2, "R$ 13.000")
    print(f"   {result.message}  patch={[p.to_dict()['span'] for p in result.patches]}")

    print("5. atualizar o arquivo .umd")
    document.save()
    for line in document.source().splitlines():
        if line.startswith("Notebook"):
            print(f"   {line}")

    print("6. reabrir e verificar a preservação")
    reopened = open_document(target)
    value = reopened.grid(table.id)[1][2]
    print(f"   valor relido: {value!r}  válido={reopened.valid}")
    ok = value == "R$ 13.000" and reopened.valid
    print("MVP OK" if ok else "MVP FALHOU")
    print(f"(cópia de trabalho em {workdir})")
    return 0 if ok else 1


def cmd_app(args) -> int:
    from .app import run_app
    return run_app(args.file)


def cmd_view(args) -> int:
    import http.server
    import webbrowser
    from .renderers.html import render_document

    doc = open_document(args.file)
    html_content = render_document(doc).encode("utf-8")

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_content)))
            self.end_headers()
            self.wfile.write(html_content)

        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"
    print(f"Visualizando {args.file} em {url} (Ctrl+C para encerrar)...")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    return 0


def cmd_install(args) -> int:
    paths = install_extension()
    print("UMD Visual Editor instalado com sucesso!")
    for p in paths:
        print(f"  -> {p}")
    print("\nReinicie ou recarregue o VS Code / Antigravity (Ctrl+Shift+P > Reload Window).")
    print("Depois disso, basta clicar em qualquer arquivo .umd para abrir no editor visual!")
    return 0


def cmd_uninstall(args) -> int:
    paths = uninstall_extension()
    print("UMD Visual Editor desinstalado:")
    for p in paths:
        print(f"  removido: {p}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="umd", description="UMD — UI Markdown")
    sub = parser.add_subparsers(dest="command", required=True)

    app_cmd = sub.add_parser("app", help="abre janela nativa de edição visual do UMD")
    app_cmd.add_argument("file")
    app_cmd.set_defaults(func=cmd_app)

    view = sub.add_parser("view", help="abre visualização do documento em memória (sem salvar HTML)")
    view.add_argument("file")
    view.set_defaults(func=cmd_view)

    install = sub.add_parser("install", help="instala o editor visual do UMD no VS Code / Antigravity")
    install.set_defaults(func=cmd_install)

    uninstall = sub.add_parser("uninstall", help="desinstala o editor visual do UMD")
    uninstall.set_defaults(func=cmd_uninstall)

    spec_cmd = sub.add_parser("spec", help="imprime referência compacta da sintaxe UMD para agentes de IA")
    spec_cmd.set_defaults(func=cmd_spec)

    install_skill_cmd = sub.add_parser("install-skill", help="instala a skill global do UMD para Antigravity, Claude e Cursor")
    install_skill_cmd.add_argument("--dir", help="pasta customizada onde gravar SKILL.md")
    install_skill_cmd.set_defaults(func=cmd_install_skill)

    check = sub.add_parser("check", help="valida um arquivo .umd")
    check.add_argument("file")
    check.add_argument("--json", action="store_true", help="saída estruturada em JSON com dicas de correção")
    check.set_defaults(func=cmd_check)

    outline = sub.add_parser("outline", help="lista títulos, tabelas, gráficos e métricas com linhas")
    outline.add_argument("file")
    outline.add_argument("--json", action="store_true", help="saída estruturada em JSON")
    outline.set_defaults(func=cmd_outline)

    add_row = sub.add_parser("add-row", help="adiciona uma linha em uma tabela ([TABLE] ou Markdown)")
    add_row.add_argument("file")
    add_row.add_argument("--table", default="1", help="índice 1-based ou id da tabela (padrão: 1)")
    add_row.add_argument("--values", help="valores separados por '|' (ex: 'Seed 133|HELD|88.0%%')")
    add_row.add_argument("--value", action="append", help="valor individual (pode repetir)")
    add_row.add_argument("--write", action="store_true", help="salva a alteração no arquivo")
    add_row.set_defaults(func=cmd_add_row)

    set_metric_cmd = sub.add_parser("set-metric", help="atualiza um [CARD title=...] ou [PROGRESS label=...]")
    set_metric_cmd.add_argument("file")
    set_metric_cmd.add_argument("--label", required=True, help="título do CARD ou label do PROGRESS")
    set_metric_cmd.add_argument("--value", required=True, help="novo valor")
    set_metric_cmd.add_argument("--subtitle", help="segunda linha opcional para [CARD]")
    set_metric_cmd.add_argument("--write", action="store_true", help="salva a alteração no arquivo")
    set_metric_cmd.set_defaults(func=cmd_set_metric)

    append_chart = sub.add_parser("append-chart", help="adiciona uma linha de dados em um [CHART]")
    append_chart.add_argument("file")
    append_chart.add_argument("--chart", default="1", help="índice 1-based, chart#N ou trecho do título")
    append_chart.add_argument("--values", help="valores separados por '|' (ex: 'Exp 133|91.5')")
    append_chart.add_argument("--value", action="append", help="valor individual (pode repetir)")
    append_chart.add_argument("--write", action="store_true", help="salva a alteração no arquivo")
    append_chart.set_defaults(func=cmd_append_chart)

    ast = sub.add_parser("ast", help="exporta a AST em JSON")
    ast.add_argument("file")
    ast.set_defaults(func=cmd_ast)

    grid = sub.add_parser("grid", help="imprime os valores de uma tabela")
    grid.add_argument("file")
    grid.add_argument("table")
    grid.set_defaults(func=cmd_grid)

    set_cell = sub.add_parser("set-cell", help="edita uma célula")
    set_cell.add_argument("file")
    set_cell.add_argument("table")
    set_cell.add_argument("row", type=int)
    set_cell.add_argument("col", type=int)
    set_cell.add_argument("value")
    set_cell.add_argument("--write", action="store_true")
    set_cell.set_defaults(func=cmd_set_cell)

    append = sub.add_parser("append-row", help="adiciona uma linha ao final da tabela")
    append.add_argument("file")
    append.add_argument("table")
    append.add_argument("--value", action="append", required=True)
    append.add_argument("--write", action="store_true")
    append.set_defaults(func=cmd_append_row)

    render = sub.add_parser("render", help="gera a versão visual do documento (HTML)")
    render.add_argument("file")
    render.add_argument("-o", "--out", help="arquivo de saída (padrão: ao lado do .umd)")
    render.set_defaults(func=cmd_render)

    demo = sub.add_parser("demo", help="executa o ciclo completo do MVP")
    demo.add_argument("file", nargs="?")
    demo.set_defaults(func=cmd_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if len(args_list) == 1 and not args_list[0].startswith("-"):
        candidate = Path(args_list[0])
        if candidate.suffix == ".umd" or candidate.exists():
            from .app import run_app
            return run_app(candidate)

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
