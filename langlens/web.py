"""Tiny dependency-free web app (standard-library HTTP server + one HTML page)."""

from __future__ import annotations

import json
import random
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from . import __version__
from .detector import analyze
from .languages import LANGUAGES, get, resolve
from .quiz import make_question
from .translate import TranslationError, translate

MAX_BODY = 100_000  # bytes
_rng = random.Random()


def _page() -> bytes:
    return resources.files("langlens").joinpath("static/index.html").read_bytes()


def handle_api(method: str, path: str, body: dict) -> tuple[int, dict]:
    """Pure request handler (easy to test without sockets)."""
    if method == "GET" and path == "/api/languages":
        return 200, {"languages": [lang._asdict() for lang in sorted(LANGUAGES.values(), key=lambda x: x.name)]}
    if method == "GET" and path == "/api/quiz":
        q = make_question(_rng)
        return 200, {
            "phrase": q.phrase,
            "answer": q.answer,
            "options": [{"code": c, "name": get(c).name, "flag": get(c).flag} for c in q.options],
        }
    if method == "GET" and path == "/api/health":
        return 200, {"status": "ok", "version": __version__}
    if method == "POST" and path == "/api/analyze":
        text = str(body.get("text", ""))
        return 200, analyze(text).to_dict()
    if method == "POST" and path == "/api/translate":
        text = str(body.get("text", ""))
        target = resolve(str(body.get("target", "en")))
        if not target:
            return 400, {"error": "unknown target language"}
        try:
            return 200, translate(text, target).to_dict()
        except TranslationError as exc:
            return 502, {"error": str(exc)}
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    server_version = f"LangLens/{__version__}"

    def log_message(self, fmt: str, *args) -> None:  # quieter console
        pass

    def _send(self, status: int, payload: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, status: int, data: dict) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send(200, _page(), "text/html; charset=utf-8")
        else:
            self._json(*handle_api("GET", path, {}))

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "text too long"})
            return
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON"})
            return
        self._json(*handle_api("POST", self.path.split("?")[0], body if isinstance(body, dict) else {}))


def serve(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"LangLens web app running at {url}  (Ctrl+C to stop)")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
