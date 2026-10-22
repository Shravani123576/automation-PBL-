"""
saarthi_automation/form_server.py
Background server manager for serving the demo form on an ephemeral localhost port.
"""

import http.server
import socket
import socketserver
import threading
from pathlib import Path
from typing import Tuple


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class DemoServerManager:
    def __init__(self, demo_form_dir: Path):
        self.demo_form_dir = demo_form_dir
        self.httpd: socketserver.TCPServer = None
        self.port: int = 0
        self.thread: threading.Thread = None

    def start(self) -> Tuple[str, int]:
        self.port = find_free_port()

        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(self.demo_form_dir), **kwargs)

            def log_message(self, format, *args):
                pass

        # Bind TCPServer
        QuietHandler.demo_form_dir = self.demo_form_dir
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("127.0.0.1", self.port), QuietHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        url = f"http://127.0.0.1:{self.port}"
        return url, self.port

    def stop(self) -> None:
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
            self.httpd = None
