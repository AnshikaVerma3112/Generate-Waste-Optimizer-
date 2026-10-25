"""Local-only HTTP server: Python API and the separate frontend folder."""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from .solver import solve, graph_data

FRONTEND = Path(__file__).resolve().parents[1] / 'frontend'
MAX_BODY = 100_000

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, format, *args):
        # Do not log uploaded data or plans.
        pass

    def reply(self, status, payload):
        body = json.dumps(payload, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/health':
            return self.reply(200, {'status': 'ok', 'engine': 'Python'})
        if path == '/api/graph':
            return self.reply(200, graph_data())
        if path.startswith('/api/'):
            return self.reply(404, {'error': 'API endpoint not found.'})
        # Only files inside frontend are served. Never expose backend/source files.
        requested = FRONTEND / unquote(path).lstrip('/')
        target = requested.resolve()
        if not target.is_relative_to(FRONTEND.resolve()):
            return self.send_error(404)
        if target.is_dir() and not (target / 'index.html').is_file():
            return self.send_error(404)
        return super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != '/api/optimize':
            return self.reply(404, {'error': 'API endpoint not found.'})
        if self.headers.get_content_type() != 'application/json':
            return self.reply(415, {'error': 'Use Content-Type: application/json.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_BODY:
                return self.reply(413, {'error': 'Request must be between 1 and 100000 bytes.'})
            data = json.loads(self.rfile.read(length))
            result = solve(data)
        except (ValueError, TypeError, KeyError, OverflowError, UnicodeError):
            # Preserve useful validation text while handling malformed structures safely.
            import sys
            error = sys.exc_info()[1]
            message = str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError) else 'Invalid request. Check the JSON and numeric fields.'
            return self.reply(400, {'error': message})
        return self.reply(200, result)

def make_server(port=8000):
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)
