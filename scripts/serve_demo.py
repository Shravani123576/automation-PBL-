"""
Simple local HTTP server using Python's built-in http.server module.
Serves the demo_form directory on localhost with an available port (default 8000).
"""

import http.server
import socketserver
import sys
from pathlib import Path


def find_free_port(preferred_port: int = 8000) -> int:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred_port))
            return preferred_port
        except OSError:
            # Pick any free ephemeral port
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def run_server(port: int = 8000):
    demo_form_dir = Path(__file__).resolve().parent.parent / "demo_form"
    if not demo_form_dir.exists():
        print(f"Error: Directory {demo_form_dir} does not exist.")
        sys.exit(1)

    port = find_free_port(port)

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(demo_form_dir), **kwargs)

        def log_message(self, format, *args):
            # Keep server console clean
            pass

    print(f"============================================================")
    print(f"SAARTHi Demo Form Server")
    print(f"Serving directory: {demo_form_dir}")
    print(f"Local URL: http://127.0.0.1:{port}/index.html")
    print(f"DEMO ONLY — NOT A REAL GOVERNMENT PORTAL")
    print(f"============================================================")

    # Allow fast address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down demo server.")


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port_arg)
