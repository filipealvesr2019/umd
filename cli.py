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
    status = _print_diagnostics(document)
    print(
        f"{len(document.nodes())} nós, {len(document.tables())} tabela(s), "
        f"{len(document.errors())} erro(s), {len(document.warnings())} aviso(s)"
    )
    return status


def cmd_outline(args) -> int:
    document = open_document(args.file)

    def walk(node, depth=0):
        pad = "  " * depth
        label = f"[{node.name}]" if node.is_component else node.type
        preview = node.text.replace("\n", " ⏎ ")[:60]
        print(f"{pad}{node.id:<14} {label:<12} L{node.line:<4} {preview}")
        for child in node.children:
            walk(child, depth + 1)

    walk(document.root)
    return _print_diagnostics(document)


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

    check = sub.add_parser("check", help="valida um arquivo .umd")
    check.add_argument("file")
    check.set_defaults(func=cmd_check)

    outline = sub.add_parser("outline", help="mostra a árvore de nós com ids e linhas")
    outline.add_argument("file")
    outline.set_defaults(func=cmd_outline)

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
