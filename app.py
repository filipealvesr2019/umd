"""Aplicativo desktop nativo do UMD (via pywebview ou navegador local).

Abre o arquivo .umd diretamente em uma janela nativa interativa estilo Notion.
Qualquer clique, edição de célula ou nova linha salva automaticamente no arquivo .umd em texto puro.
Zero arquivos HTML gerados no disco.
"""
from __future__ import annotations

import base64
from pathlib import Path


class UmdBridge:
    """Ponte entre a interface visual e o arquivo .umd no disco."""

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def save(self, text: str) -> bool:
        try:
            self.file_path.write_text(text, encoding="utf-8")
            return True
        except Exception as exc:
            print(f"Erro ao salvar: {exc}")
            return False

    def load(self) -> str:
        if self.file_path.exists():
            return self.file_path.read_text(encoding="utf-8")
        return ""


def build_html(file_path: Path) -> str:
    """Gera a página HTML interativa usando o template visual oficial do UMD."""
    content = ""
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
    
    if not content.strip():
        content = (
            f"# {file_path.stem.capitalize()}\n\n"
            "Documento interativo UMD.\n\n"
            "[TABLE title=\"Tabela de Dados\"]\n"
            "Item | Quantidade | Valor\n"
            "Exemplo | 1 | R$ 100\n"
            "[/TABLE]\n"
        )
        file_path.write_text(content, encoding="utf-8")

    b64_content = base64.b64encode(content.encode("utf-8")).decode("ascii")
    template_path = Path(__file__).resolve().parent / "editor.html"
    template = template_path.read_text(encoding="utf-8")
    return template.replace("__INITIAL_CONTENT_BASE64__", b64_content)


def run_app(file_path: str | Path) -> int:
    """Inicia a janela nativa do UMD."""
    target = Path(file_path).resolve()
    bridge = UmdBridge(target)
    html_doc = build_html(target)

    try:
        import webview
        window = webview.create_window(
            title=f"UMD — {target.name}",
            html=html_doc,
            js_api=bridge,
            width=920,
            height=750,
            min_size=(640, 500)
        )
        webview.start()
        return 0
    except Exception as exc:
        # Fallback para servidor local se WebView2 não estiver disponível
        import http.server
        import webbrowser

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = html_doc.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                if self.path == "/api/save":
                    length = int(self.headers.get("Content-Length", 0))
                    raw_text = self.rfile.read(length).decode("utf-8")
                    bridge.save(raw_text)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"ok")

            def log_message(self, *args):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        port = server.server_address[1]
        url = f"http://127.0.0.1:{port}"
        print(f"Abrindo UMD em {url}...")
        webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        return 0
