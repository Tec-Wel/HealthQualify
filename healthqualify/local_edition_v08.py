"""HealthQualify Local Edition: private-first guided synthetic qualification journey.

No CLI access-token copying, cloud account, paid API, or LLM required. This is
a loopback-only engineering alpha. Session cookies are opaque/HttpOnly; writes
require a same-origin custom CSRF header; all operations use local credentials.
Not a clinical system, validated QMS, or a regulated e-signature service.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import os
import secrets
import socket
import threading
import time
import webbrowser
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .security import IdentityStore, AuthenticationError
from .workspace import Workspace
from .agents import AGENTS, investigate
from .agent_runtime_v07 import ScopedAgentRuntime
from .assurance import encode, digest

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/"examples"/"synthetic_lis_v2"/"protocol.json"
DEMO_V3=ROOT/"examples"/"synthetic_lis_v3"/"protocol.json"
UI=Path(__file__).with_name("local_ui_v08.html")
MODEL="qwen3:8b"
LIMIT=32*1024


def _read_document(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _demo_protocol(doc,system_id):
    updated=json.loads(json.dumps(doc))
    updated["system"]["id"]=system_id
    return updated


def _single_run(db,username):
    """Create isolated synthetic example and execute its predefined checks."""
    work=Workspace(db)
    try:
        system=work.add_system("Synthetic LIS demonstration",
                               "Educational qualification of fictional LIS interfaces",username)
        payload=_demo_protocol(_read_document(DEMO),system["id"])
        protocol=work.draft_protocol(system["id"],payload,username)
        # This is an EXPLICIT technical demo state, not QA sign-off.
        # Workspaces normally require independent QA baselines. The local
        # onboarding journey performs a clearly marked draft execution.
        run=work.execute(protocol["id"],username,allow_draft=True)
        return {"system":system,"protocol":{"id":protocol["id"],"version":protocol["version"],
                    "state":protocol["state"]},"run":{"id":run["id"],
                    "summary":run["results"]["summary"],
                    "traceability":run["results"]["traceability"],
                    "tests":run["results"]["results"]},
                "deviations":[d for d in work.list("deviations")
                              if d["run_id"]==run["id"]],
                "technical_demo":True,"qualification_approved":False}
    finally:
        work.close()


class LocalServer(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,host,port,database,allow_model=False):
        if host!="127.0.0.1":
            raise ValueError("Local Edition must bind only to IPv4 loopback")
        self.database=str(database)
        self.allow_model=bool(allow_model)
        self.csrf_secret=secrets.token_bytes(32)
        super().__init__((host,port),LocalHandler)


class LocalHandler(BaseHTTPRequestHandler):
    server_version="HealthQualifyLocal/0.8"
    def log_message(self,fmt,*args):
        # Avoid writing credentials, query params, or content to logs.
        return

    def headers_safe(self):
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Cross-Origin-Resource-Policy","same-origin")
        self.send_header("Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self'; base-uri 'none'; "
            "form-action 'self'; frame-ancestors 'none'")

    def response(self,status,payload,extra=None,content_type="application/json; charset=utf-8"):
        data=(json.dumps(payload,sort_keys=True).encode("utf-8") if
              content_type.startswith("application/json") else payload)
        self.send_response(status)
        self.send_header("Content-Type",content_type)
        self.headers_safe()
        if extra:
            for k,v in extra.items():
                self.send_header(k,v)
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def origin_check(self):
        # Check origin and also the host for DNS rebinding. Custom header
        # blocks cross-site form writes even when Origin is omitted.
        host=self.headers.get("Host","")
        allowed="127.0.0.1:"+str(self.server.server_port)
        if host!=allowed:
            raise PermissionError("Host denied")
        origin=self.headers.get("Origin")
        if origin is not None and origin!="http://"+allowed:
            raise PermissionError("Cross-origin request denied")

    def body(self):
        try:
            length=int(self.headers.get("Content-Length","0"))
        except ValueError:
            raise ValueError("Invalid length")
        if not 0<length<=LIMIT:
            raise ValueError("Invalid request body size")
        data=json.loads(self.rfile.read(length))
        if not isinstance(data,dict):
            raise ValueError("Expected JSON object")
        return data

    def cookie_token(self):
        jar=cookies.SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie",""))
        except cookies.CookieError:
            return ""
        return jar["hq_session"].value if "hq_session" in jar else ""

    def principal(self,permission="read"):
        token=self.cookie_token()
        store=IdentityStore(self.server.database)
        try:
            principal=store.authenticate(token)
            store.authorize(principal,permission)
            return principal
        finally:
            store.close()

    def csrf(self):
        token=self.cookie_token()
        if not token:
            raise AuthenticationError("Session required")
        return hmac.new(self.server.csrf_secret,token.encode(),hashlib.sha256).hexdigest()

    def mutation_check(self):
        if self.headers.get("X-HQ-Request")!="1":
            raise PermissionError("Required request header missing")
        if not hmac.compare_digest(self.headers.get("X-HQ-CSRF",""),self.csrf()):
            raise PermissionError("CSRF validation failed")

    def do_GET(self):
        try:
            self.origin_check()
            path=urlsplit(self.path).path
            if path=="/":
                return self.response(200,UI.read_bytes(),content_type="text/html; charset=utf-8")
            if path=="/local-ui.js":
                script=UI.with_name("local_ui_v08.js")
                return self.response(200,script.read_bytes(),content_type="text/javascript; charset=utf-8")
            if path=="/api/health":
                return self.response(200,{"status":"ok","network":"loopback-only",
                                          "llm_required":False,"clinical_use":False})
            if path=="/api/setup":
                store=IdentityStore(self.server.database)
                try:
                    available=store.conn.execute("SELECT 1 FROM hq_identities LIMIT 1").fetchone() is None
                finally:store.close()
                return self.response(200,{"needs_setup":available})
            if path=="/api/session":
                principal=self.principal()
                return self.response(200,{"user":principal,"csrf":self.csrf()})
            principal=self.principal()
            if path=="/api/overview":
                work=Workspace(self.server.database)
                try:
                    systems=work.list("systems")
                    protocols=work.list("protocols")
                    runs=work.list("runs")
                    deviations=work.list("deviations")
                    return self.response(200,{
                        "systems":[{"id":s["id"],"name":s["name"]} for s in systems],
                        "protocols":[{"id":p["id"],"system_id":p["system_id"],
                                      "version":p["version"],"state":p["state"]} for p in protocols],
                        "runs":[{"id":r["id"],"protocol_id":r["protocol_id"],
                                 "summary":r["results"]["summary"],
                                 "traceability":r["results"]["traceability"],
                                 "results":r["results"]["results"]} for r in runs[:15]],
                        "deviations":[{"id":d["id"],"run_id":d["run_id"],
                                       "test_id":d["test_id"],"status":d["status"],
                                       "kind":d["kind"]} for d in deviations[:50]],
                        "qualification_approved":False})
                finally:work.close()
            if path=="/api/model":
                # No contact with Ollama on regular page loads. Explicit
                # user action triggers model availability checks.
                return self.response(200,{"enabled":self.server.allow_model,
                                          "model":MODEL,"installed":None,
                                          "required":False,"cost_per_api_token":0})
            if path=="/api/reviews":
                runtime=ScopedAgentRuntime(self.server.database)
                try:
                    systems=runtime.workspace.list("systems")
                    entries=[]
                    token=self.cookie_token()
                    for s in systems:
                        try:
                            entries.extend(runtime.review_queue(token,s["id"],limit=15))
                        except AuthenticationError:
                            continue
                    return self.response(200,{"reviews":entries[:50]})
                finally:runtime.close()
            return self.response(404,{"error":"not_found"})
        except (AuthenticationError,PermissionError):
            self.response(403,{"error":"access_denied"})
        except Exception:
            self.response(500,{"error":"internal_error"})

    def do_POST(self):
        try:
            self.origin_check()
            path=urlsplit(self.path).path
            if self.headers.get("X-HQ-Request")!="1":
                raise PermissionError("Missing request marker")
            data=self.body()
            if path=="/api/bootstrap":
                if set(data)!={"username","password"}:
                    raise ValueError("Only username/password allowed")
                store=IdentityStore(self.server.database)
                try:
                    user=store.bootstrap(data["username"],data["password"])
                finally:store.close()
                return self.response(201,{"created":True,"username":user["username"]})
            if path=="/api/login":
                if set(data)!={"username","password"}:
                    raise ValueError("Only username/password allowed")
                store=IdentityStore(self.server.database)
                try:
                    token=store.login(data["username"],data["password"])
                    user=store.authenticate(token)
                finally:store.close()
                cookie="hq_session="+token+"; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600"
                return self.response(200,{"user":user,"csrf":hmac.new(
                    self.server.csrf_secret,token.encode(),hashlib.sha256).hexdigest()},
                    extra={"Set-Cookie":cookie})
            self.mutation_check()
            principal=self.principal()
            if path=="/api/logout":
                store=IdentityStore(self.server.database)
                try:store.logout(self.cookie_token())
                finally:store.close()
                return self.response(200,{"logged_out":True},extra={
                    "Set-Cookie":"hq_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"})
            if path=="/api/users":
                if set(data)!={"username","password","role"}:
                    raise ValueError("Username, password and role required")
                store=IdentityStore(self.server.database)
                try:
                    store.authorize(principal,"users")
                    result=store.create_user(principal,data["username"],
                                             data["password"],data["role"])
                finally:store.close()
                return self.response(201,result)
            if path=="/api/grants":
                if set(data)!={"username","system_id"}:
                    raise ValueError("Username and system required")
                runtime=ScopedAgentRuntime(self.server.database)
                try:
                    result=runtime.grant_system(self.cookie_token(),
                                                data["username"],data["system_id"])
                    return self.response(201,result)
                finally:runtime.close()
            if path=="/api/demo":
                if data not in ({},):
                    raise ValueError("Demo requires empty JSON")
                if principal["role"] not in {"admin","validator"}:
                    raise AuthenticationError("Only engineering users can run demo")
                return self.response(201,_single_run(self.server.database,principal["username"]))
            if path=="/api/agent":
                if set(data)!={"system_id","agent"} or data["agent"] not in AGENTS:
                    raise ValueError("Invalid agent request")
                runtime=ScopedAgentRuntime(self.server.database)
                try:
                    system_id=data["system_id"]
                    sample=_demo_protocol(_read_document(DEMO_V3),system_id)
                    registry={"systems":[{"id":system_id,"components":[
                        "healthqualify/healthcare.py","healthqualify/assurance.py"]}]}
                    report=runtime.analyze(self.cookie_token(),system_id,sample,
                        data["agent"],changed_files=["healthqualify/healthcare.py"],
                        registry=registry)
                    return self.response(201,report)
                finally:runtime.close()
            if path=="/api/review":
                if set(data)!={"observation_id","decision","rationale"}:
                    raise ValueError("Invalid review fields")
                runtime=ScopedAgentRuntime(self.server.database)
                try:
                    result=runtime.review(self.cookie_token(),data["observation_id"],
                                          data["decision"],data["rationale"])
                    return self.response(200,result)
                finally:runtime.close()
            if path=="/api/model-explain":
                # Explicit user click and server opt-in required. Only existing
                # redacted findings are sent to the local pinned Ollama endpoint.
                if not self.server.allow_model:
                    raise PermissionError("Local Qwen disabled by server policy")
                if set(data)!={"observation_id"} or not isinstance(data["observation_id"],str):
                    raise ValueError("Existing observation ID required")
                runtime=ScopedAgentRuntime(self.server.database)
                try:
                    row=runtime.conn.execute("""SELECT system_id,agent,report,report_digest
                        FROM agent_observations WHERE id=?""",
                        (data["observation_id"],)).fetchone()
                    if not row:
                        raise ValueError("Unknown observation")
                    runtime._principal(self.cookie_token(),row["system_id"],"read")
                    if digest(row["report"].encode())!=row["report_digest"]:
                        raise ValueError("Stored observation integrity failed")
                    report=json.loads(row["report"])
                    explanation_input=json.dumps({
                        "agent":row["agent"],"summary":report["summary"],
                        "findings":report["findings"]},sort_keys=True)
                    if len(explanation_input)>11000:
                        raise ValueError("Agent context is too large")
                    from .ai import local_draft
                    narrative=local_draft(row["agent"],explanation_input,MODEL,consent=True)
                    return self.response(200,{"observation_id":data["observation_id"],
                        "model":MODEL,"text":narrative["text"],
                        "status":"DRAFT_UNVERIFIED","human_review_required":True,
                        "qualification_approved":False,
                        "deterministic_report_sha256":row["report_digest"]})
                finally:runtime.close()
            if path=="/api/model-check":
                if data not in ({},):
                    raise ValueError("Unexpected input")
                if not self.server.allow_model:
                    return self.response(200,{"available":False,"reason":"opt_in_required"})
                # Local, bounded connectivity check. Never download a model.
                from urllib.request import urlopen
                try:
                    with urlopen("http://127.0.0.1:11434/api/tags",timeout=2) as resp:
                        raw=resp.read(16385)
                    if len(raw)>16384:
                        raise ValueError("Model registry reply oversized")
                    listing=json.loads(raw)
                    names=[m.get("name","") for m in listing.get("models",[])
                           if isinstance(m,dict)]
                    return self.response(200,{"available":MODEL in names,
                        "installed_models":len(names),"target":MODEL,
                        "notice":"Availability is not evidence of validated inference"})
                except (OSError,ValueError,TypeError):
                    return self.response(200,{"available":False,"reason":"ollama_unavailable"})
            return self.response(404,{"error":"not_found"})
        except (AuthenticationError,PermissionError):
            self.response(403,{"error":"access_denied"})
        except (KeyError,ValueError,TypeError,json.JSONDecodeError):
            self.response(400,{"error":"invalid_request"})
        except Exception:
            self.response(500,{"error":"internal_error"})


def main(argv=None):
    p=argparse.ArgumentParser(description="HealthQualify Local Edition — offline-first developer alpha")
    p.add_argument("--db",default=None)
    p.add_argument("--port",type=int,default=8899)
    p.add_argument("--allow-local-qwen",action="store_true")
    p.add_argument("--no-browser",action="store_true")
    args=p.parse_args(argv)
    location=Path(args.db or Path.home()/".healthqualify"/"local-edition.db").expanduser()
    location.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    server=LocalServer("127.0.0.1",args.port,location,args.allow_local_qwen)
    address="http://127.0.0.1:"+str(server.server_port)
    print("HealthQualify Local Edition: "+address)
    print("Synthetic developer alpha. No PHI, no mandatory LLM or cloud account.")
    try:
        if not args.no_browser:
            threading.Timer(0.4,lambda:webbrowser.open(address)).start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__=="__main__":
    main()
