"""Authenticated single-site REST API for demonstration deployments.

Binds only loopback. TLS, OIDC/MFA, tenant partitioning, rate limiting,
regulated signing and PHI controls are deployment/validation work still required.
"""
from __future__ import annotations
import json
import os
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit
from .workspace import Workspace
from .security import IdentityStore, AuthenticationError
from .regulatory import list_controls

def make_handler(work: Workspace, identities: IdentityStore):
    class Handler(BaseHTTPRequestHandler):
        server_version="HealthQualifySecureAlpha/0.4"

        def log_message(self,*args):
            pass

        def respond(self,code: int, payload):
            body=json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()
            self.send_response(code)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'none'")
            self.send_header("Referrer-Policy","no-referrer")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def principal(self,permission: str):
            auth=self.headers.get("Authorization","")
            if not auth.startswith("Bearer "):
                raise AuthenticationError("Authorization required")
            who=identities.authenticate(auth[7:])
            identities.authorize(who,permission)
            return who

        def parse_body(self):
            try:
                size=int(self.headers.get("Content-Length","0"))
            except ValueError:
                raise ValueError("Invalid content length")
            if not 0<size<=1024*1024:
                raise ValueError("Body exceeds limit")
            body=json.loads(self.rfile.read(size))
            if not isinstance(body,dict):
                raise ValueError("JSON object required")
            return body

        def dispatch(self,write=False):
            path=urlsplit(self.path).path
            if path=="/health" and not write:
                return self.respond(200,{"status":"ok","type":"secure-alpha","regulated":False})
            try:
                if write and path=="/login":
                    obj=self.parse_body()
                    token=identities.login(obj.get("username"),obj.get("password"))
                    return self.respond(200,{"access_token":token,"token_type":"Bearer","expires_in":3600})
                if write:
                    if path=="/logout":
                        self.principal("read")
                        identities.logout(self.headers["Authorization"][7:])
                        return self.respond(200,{"revoked":True})
                    if path=="/users":
                        actor=self.principal("users")
                        obj=self.parse_body()
                        return self.respond(201,identities.create_user(actor,obj["username"],obj["password"],obj["role"]))
                    if path=="/systems":
                        actor=self.principal("write")
                        obj=self.parse_body()
                        return self.respond(201,work.add_system(obj["name"],obj["intended_use"],actor["username"]))
                    if path=="/protocols":
                        actor=self.principal("write")
                        obj=self.parse_body()
                        return self.respond(201,work.draft_protocol(obj["system_id"],obj["payload"],actor["username"]))
                    if path=="/baselines":
                        actor=self.principal("baseline")
                        obj=self.parse_body()
                        return self.respond(200,work.baseline(obj["protocol_id"],actor["username"],obj["rationale"]))
                    if path=="/runs":
                        actor=self.principal("execute")
                        obj=self.parse_body()
                        return self.respond(201,work.execute(obj["protocol_id"],actor["username"],False))
                    return self.respond(404,{"error":"not_found"})
                principal=self.principal("audit" if path=="/audit" else "read")
                if path=="/frameworks":
                    return self.respond(200,list_controls())
                if path=="/audit":
                    return self.respond(200,work.audit_events())
                tables={"/systems":"systems","/protocols":"protocols","/runs":"runs","/deviations":"deviations"}
                if path in tables:
                    return self.respond(200,work.list(tables[path]))
                return self.respond(404,{"error":"not_found"})
            except AuthenticationError:
                return self.respond(403,{"error":"authentication_or_permission_denied"})
            except KeyError:
                return self.respond(404,{"error":"missing_reference_or_field"})
            except (ValueError,TypeError,json.JSONDecodeError):
                return self.respond(400,{"error":"invalid_request"})
            except Exception:
                # Do not leak implementation internals or sensitive data.
                return self.respond(500,{"error":"server_error"})

        def do_GET(self):
            self.dispatch(False)
        def do_POST(self):
            self.dispatch(True)
    return Handler

def serve_secure(database: str, host: str="127.0.0.1", port: int=8877):
    if host not in {"127.0.0.1","::1"}:
        raise ValueError("Secure alpha must bind to loopback only")
    work=Workspace(database)
    ident=IdentityStore(database)
    server=HTTPServer((host,port),make_handler(work,ident))
    try:
        print(f"HealthQualify authenticated local API: http://{host}:{port}")
        server.serve_forever()
    finally:
        server.server_close()
        ident.close()
        work.close()
