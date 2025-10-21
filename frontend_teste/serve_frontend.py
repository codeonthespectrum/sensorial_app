"""
Servidor HTTP simples para servir o frontend
Execute: python3 serve_frontend.py
Acesso: http://localhost:3000
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = 3000
FRONTEND_DIR = Path(__file__).parent / "frontend"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Adicionar headers para evitar cache
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(FRONTEND_DIR)
    
    handler = MyHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"")
    print(f"╔════════════════════════════════════════╗")
    print(f"║  Frontend Server Rodando               ║")
    print(f"║  http://localhost:{PORT:<25} ║")
    print(f"║  (Abra no seu navegador)              ║")
    print(f"╚════════════════════════════════════════╝")
    print(f"")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Servidor encerrado!")
        httpd.server_close()
