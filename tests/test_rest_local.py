"""Synthetic-only loopback REST checker safety and result tests."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from healthqualify.rest_local import check_local_json


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/data")
            self.end_headers()
            return
        data = json.dumps({"status": "ready", "nested": {"count": 2}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class LocalRestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=2)

    def test_expected_values(self):
        self.assertEqual(check_local_json(self.base + "/data", "status", "ready", True)["status"], "PASS")
        self.assertEqual(check_local_json(self.base + "/data", "status", "bad", True)["status"], "FAIL")
        self.assertEqual(check_local_json(self.base + "/data", "nested.count", 2, True)["status"], "PASS")
        self.assertEqual(check_local_json(self.base + "/data", "missing", 1, True)["status"], "FAIL")

    def test_fail_closed(self):
        for url in ("https://example.com/", "http://localhost:80/", "http://127.0.0.1:8000/?token=x",
                    "http://127.0.0.1:8000/#abc"):
            with self.assertRaises(ValueError):
                check_local_json(url, "status", "ready", True)
        with self.assertRaises(ValueError):
            check_local_json(self.base + "/data", "status", "ready")
        with self.assertRaises(ValueError):
            check_local_json(self.base + "/redirect", "status", "ready", True)
