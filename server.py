#!/usr/bin/env python3
"""
Quiz Server
-----------
Serves quiz.html and saves scores to scores.csv.

Usage:
    python server.py

Then open: http://localhost:8080
"""

import csv
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8080))
HTML_FILE = os.path.join(os.path.dirname(__file__), "quiz.html")
CSV_FILE  = os.path.join(os.path.dirname(__file__), "scores.csv")


def ensure_csv():
    """Create CSV with header row if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Score", "Timestamp"])


class QuizHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} → {fmt % args}")

    # ── GET ──────────────────────────────────────────────────────
    def do_GET(self):
        if self.path in ("/", "/index.html", "/quiz.html"):
            self._serve_file(HTML_FILE, "text/html")
        elif self.path == "/scores":
            self._serve_scores()
        else:
            self._send(404, "text/plain", b"Not found")

    def _serve_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                data = f.read()
            self._send(200, content_type, data)
        except FileNotFoundError:
            self._send(404, "text/plain", b"quiz.html not found next to server.py")

    def _serve_scores(self):
        """Return all saved scores as JSON."""
        ensure_csv()
        rows = []
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        data = json.dumps(rows, indent=2).encode()
        self._send(200, "application/json", data)

    # ── POST ─────────────────────────────────────────────────────
    def do_POST(self):
        if self.path == "/save_score":
            self._save_score()
        else:
            self._send(404, "text/plain", b"Not found")

    def _save_score(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = self.rfile.read(length)
            data   = json.loads(body)

            name  = str(data.get("name", "")).strip()[:100]
            score = int(data.get("score", 0))

            if not name:
                self._send(400, "text/plain", b"Name is required")
                return

            ensure_csv()
            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([name, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

            print(f"  ✓ Saved: {name} → {score}/40")
            self._send(200, "application/json", json.dumps({"ok": True}).encode())

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            self._send(400, "text/plain", f"Bad request: {e}".encode())

    # ── HELPERS ──────────────────────────────────────────────────
    def _send(self, status, content_type, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    ensure_csv()
    server = HTTPServer(("0.0.0.0", PORT), QuizHandler)
    print("=" * 50)
    print(f"  Quiz Server running at http://localhost:{PORT}")
    print(f"  Scores saved to: {CSV_FILE}")
    print(f"  View scores at:  http://localhost:{PORT}/scores")
    print("  Press Ctrl+C to stop.")
    print("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
