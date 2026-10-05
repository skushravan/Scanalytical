import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000
DIRECTORY = os.path.join(os.path.dirname(__file__), "website")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    print("=" * 65)
    print("  SONAR // GLOBAL CONCERT TURNOUT INTELLIGENCE DASHBOARD")
    print("=" * 65)
    print(f"  Serving dashboard at: http://localhost:{PORT}")
    print(f"  Root directory:       {DIRECTORY}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)

    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped gracefully.")

if __name__ == "__main__":
    start_server()
