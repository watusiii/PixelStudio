"""Run: python serve.py   then open http://localhost:8000   (no caching, so new exports show on reload)."""
import http.server, os, socketserver, webbrowser

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

NoCache.extensions_map.update({".js": "text/javascript"})
with socketserver.TCPServer(("", 8000), NoCache) as httpd:
    print("VaniaGraybox on http://localhost:8000  (Ctrl+C to stop)")
    webbrowser.open("http://localhost:8000")
    httpd.serve_forever()
