"""Minimal local development HTTP API and read-only HTML dashboard.

Not production ready: no TLS, enterprise IAM, CSRF protection or validated signatures.
State mutations require a locally configured bearer token and loopback binding.
"""
from __future__ import annotations
import hmac
import json
import os
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from .workspace import Workspace
from .regulatory import list_controls

def create_handler(workspace: Workspace, token: str):
    class Handler(BaseHTTPRequestHandler):
        server_version="HealthQualifyDev/0.3"

        def log_message(self, fmt, *args):
            # Avoid logging patient-like/request bodies or bearer tokens.
            pass

        def send(self, code: int, data, ctype: str = "application/json"):
            body=(json.dumps(data,sort_keys=True).encode("utf-8") if ctype=="application/json"
                  else str(data).encode("utf-8"))
            self.send_response(code)
            self.send_header("Content-Type",ctype+"; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'none'; style-src 'unsafe-inline'")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path=urlparse(self.path).path
            if path=="/api/health":
                return self.send(200,{"status":"ok","mode":"development","qualification_approved":False})
            if path=="/api/frameworks":
                return self.send(200,list_controls())
            if path in ("/api/systems","/api/protocols","/api/runs","/api/deviations"):
                return self.send(200,workspace.list(path.removeprefix("/api/")))
            if path=="/":
                systems=workspace.list("systems",20)
                runs=workspace.list("runs",10)
                deviations=workspace.list("deviations",50)
                cards="".join("<li>"+escape(x["name"])+" — "+escape(x["intended_use"])+"</li>" for x in systems)
                info="".join("<li>"+escape(x["id"])[:12]+" — "+escape(str(x["results"]["summary"]))+"</li>" for x in runs)
                page=("<!doctype html><html lang='en'><meta charset='utf-8'><title>HealthQualify</title>"
                      "<style>body{font:16px system-ui;max-width:900px;margin:40px auto;background:#f8fafb;color:#132f3a}"
                      "section{background:white;padding:20px;border-radius:12px;margin-bottom:16px}"
                      "small{color:#596c71}</style><h1>HealthQualify</h1>"
                      "<p>Local development dashboard — not a qualified regulated system</p>"
                      "<section><h2>Systems ("+str(len(systems))+")</h2><ul>"+cards+"</ul></section>"
                      "<section><h2>Recent execution runs</h2><ul>"+info+"</ul></section>"
                      "<section><h2>Recorded deviations</h2><p>"+str(len(deviations))+
                      " entries in local workspace</p></section><small>API: /api/frameworks, /api/systems, /api/runs. "
                      "No PHI or production systems. No regulatory approvals.</small></html>")
                return self.send(200,page,"text/html")
            return self.send(404,{"error":"not_found"})

        def do_POST(self):
            path=urlparse(self.path).path
            bearer=self.headers.get("Authorization","")
            if not token or not hmac.compare_digest(bearer,"Bearer "+token):
                return self.send(401,{"error":"authorization_required"})
            try:
                length=int(self.headers.get("Content-Length","0"))
                if length<=0 or length>1024*1024:
                    return self.send(413,{"error":"invalid_body_size"})
                payload=json.loads(self.rfile.read(length))
                if not isinstance(payload,dict):
                    raise ValueError("JSON object required")
                if path=="/api/systems":
                    data=workspace.add_system(payload["name"],payload["intended_use"],payload["owner"])
                elif path=="/api/protocols":
                    data=workspace.draft_protocol(payload["system_id"],payload["protocol"],payload["actor"])
                elif path=="/api/runs":
                    data=workspace.execute(payload["protocol_id"],payload["actor"],
                                           allow_draft=False)
                else:
                    return self.send(404,{"error":"not_found"})
                return self.send(201,data)
            except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
                return self.send(400,{"error":"invalid_request","detail":str(exc)})
    return Handler

def serve(database: str, host="127.0.0.1",port=8765, token=None):
    if host not in {"127.0.0.1","::1","localhost"}:
        raise ValueError("Development server must bind only to loopback")
    if not token or len(token)<24:
        raise ValueError("Set HEALTHQUALIFY_API_TOKEN with at least 24 random characters")
    workspace=Workspace(database)
    server=ThreadingHTTPServer((host,port),create_handler(workspace,token))
    try:
        print(f"HealthQualify local development API: http://{host}:{port}")
        server.serve_forever()
    finally:
        server.server_close()
        workspace.close()
