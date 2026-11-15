"""Loopback-only, authenticated developer dashboard for five advisory agents.

Run only with synthetic demo protocols. The one-user local token is *not*
enterprise SSO/MFA or Part 11 electronic-signature infrastructure.
"""
from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .agent_orchestrator import AgentHistory
from .agents import AGENTS

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>HealthQualify · Local AI Agents</title>
<style>
:root{font:15px system-ui,Segoe UI,Arial,sans-serif;color:#172944;background:#f3f7fa}
*{box-sizing:border-box}body{max-width:1160px;margin:0 auto;padding:30px}
header{display:flex;align-items:center;justify-content:space-between;gap:12px}
h1{margin:0;font-size:28px}small,.muted{color:#64748b}.pill{border-radius:24px;padding:7px 12px;background:#d9f3ed;color:#075f53;font-weight:700}
.panel{background:white;border:1px solid #dce5ed;border-radius:14px;padding:22px;margin-top:20px;box-shadow:0 6px 20px #0f27430b}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.agent{border:1px solid #dce5ed;border-radius:12px;padding:18px;background:#fff}
.agent h3{margin:6px 0;font-size:17px}.agent p{color:#475569;min-height:50px}
button{background:#0d766b;border:0;color:white;padding:11px 17px;border-radius:8px;cursor:pointer;font-weight:650}
button:hover{background:#09594f}button:disabled{opacity:.5;cursor:wait}
input{padding:11px;border:1px solid #bccad8;border-radius:8px;max-width:100%;width:360px}
#result{white-space:pre-wrap;overflow-wrap:anywhere;max-height:480px;overflow:auto;background:#10253f;color:#e8f7ff;padding:20px;border-radius:10px}
table{border-collapse:collapse;width:100%}td,th{padding:11px;text-align:left;border-bottom:1px solid #e5edf3}
.notice{padding:13px;background:#fff7e6;border-left:4px solid #d09b32;border-radius:6px}
@media(max-width:620px){body{padding:12px}header{display:block}table{font-size:12px}}
</style></head><body>
<header><div><h1>HealthQualify <span style="color:#0d766b">AI Agents</span></h1><p class="muted">Five offline qualification investigators · synthetic developer alpha</p></div><div class="pill">LOCAL · DRAFT ONLY</div></header>
<div class="notice"><strong>Not a regulated approval system.</strong> Findings are advisory, model explanations are unverified, and QA release authorization is not supported.</div>
<section class="panel"><h2>Local access</h2><p>Enter the token configured for this workstation. It is kept in this page's memory only.</p>
<input id="token" type="password" autocomplete="off" placeholder="Local dashboard token"> <button onclick="refresh()">Load history</button>
<p class="muted">Default: deterministic analysis, with no model or network call.</p></section>
<section class="panel"><h2>Investigate your synthetic protocol</h2><p class="muted">The dashboard uses server-configured, allowlisted demo files. It does not accept arbitrary file paths.</p>
<div class="grid" id="agents"></div><p><button id="runall" onclick="run('all')">Run all five agents</button></p></section>
<section class="panel"><h2>Run results</h2><div id="result" role="status">Select an agent to generate a draft finding.</div></section>
<section class="panel"><h2>Local investigation history</h2><table><thead><tr><th>Agent</th><th>State</th><th>Created (UTC)</th><th>Job ID</th></tr></thead><tbody id="history"></tbody></table></section>
<script>
const items=[
["release-impact","Release Impact Investigator","Maps changed components to tests and conservatively flags unknown impact."],
["gap-hunter","Qualification Gap Hunter","Detects missing mapping and evidence gaps."],
["failure-investigation","Failure Investigation Copilot","Reviews verified non-passing test outcomes."],
["qa-readiness","QA Evidence Readiness","Flags incomplete evidence and review blockers."],
["dependency-investigator","Cross-System Dependency Investigator","Traces changed components across registered systems."]];
document.querySelector("#agents").replaceChildren(...items.map(([id,name,description])=>{
 const card=document.createElement("article");card.className="agent";
 const h=document.createElement("h3");h.textContent=name;
 const p=document.createElement("p");p.textContent=description;
 const b=document.createElement("button");b.textContent="Run investigation";b.onclick=()=>run(id);
 card.append(h,p,b);return card;
}));
async function request(path,body){
 const headers={"Authorization":"Bearer "+document.querySelector("#token").value};
 if(body!==undefined)headers["Content-Type"]="application/json";
 const res=await fetch(path,{method:body===undefined?"GET":"POST",headers,
  body:body===undefined?undefined:JSON.stringify(body),cache:"no-store"});
 const result=await res.json();if(!res.ok)throw new Error(result.error||"Request failed");
 return result;
}
async function run(agent){
 const buttons=document.querySelectorAll("button");buttons.forEach(b=>b.disabled=true);
 try{const result=await request("/api/run",{agent});
 document.querySelector("#result").textContent=JSON.stringify(result,null,2);
 await refresh();
 }catch(e){document.querySelector("#result").textContent="Error: "+e.message}
 finally{buttons.forEach(b=>b.disabled=false)}
}
async function refresh(){
 try{const data=await request("/api/jobs");const table=document.querySelector("#history");
 table.replaceChildren(...data.jobs.map(j=>{
  const tr=document.createElement("tr");
  [j.agent,j.state,j.created_at,j.job_id].forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.append(td)});return tr;
 }));}catch(e){document.querySelector("#result").textContent="History error: "+e.message}
}
</script></body></html>"""


def make_handler(history, token, protocol, registry, changed, evidence_dir=None, trusted_sha=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def reply(self, code, data):
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            for k, v in (("Content-Type", "application/json; charset=utf-8"),
                         ("Cache-Control", "no-store"),
                         ("X-Content-Type-Options", "nosniff"),
                         ("Referrer-Policy", "no-referrer"),
                         ("Content-Security-Policy", "default-src 'none'"),
                         ("Content-Length", str(len(body)))):
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            value = self.headers.get("Authorization", "")
            return hmac.compare_digest(value, "Bearer " + token)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/" or path == "/index.html":
                body = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'")
                self.send_header("X-Frame-Options", "DENY")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if not self.authorized():
                return self.reply(403, {"error": "Unauthorized"})
            if path == "/api/jobs":
                return self.reply(200, {"jobs": history.list(), "chain_head": history.chain_head()})
            return self.reply(404, {"error": "Not found"})

        def do_POST(self):
            if not self.authorized():
                return self.reply(403, {"error": "Unauthorized"})
            if urlsplit(self.path).path != "/api/run":
                return self.reply(404, {"error": "Not found"})
            origin = self.headers.get("Origin")
            if origin and origin not in ("http://127.0.0.1:" + str(self.server.server_port),
                                         "http://localhost:" + str(self.server.server_port)):
                return self.reply(403, {"error": "Origin not authorized"})
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= 4096:
                    raise ValueError("Invalid request length")
                payload = json.loads(self.rfile.read(n))
                if not isinstance(payload, dict) or set(payload) != {"agent"}:
                    raise ValueError("Only agent selection is accepted")
                agent = payload["agent"]
                if agent != "all" and agent not in AGENTS:
                    raise ValueError("Unknown agent")
                kw = {"changed_files": changed, "registry_path": registry,
                      "evidence_dir": evidence_dir, "trusted_manifest_sha256": trusted_sha,
                      "use_ollama": False}
                if agent == "all":
                    data = history.run_all("local_dashboard", protocol, **kw)
                else:
                    data = history.run("local_dashboard", agent, protocol, **kw)
                return self.reply(200, data)
            except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
                return self.reply(400, {"error": str(exc)[:200]})
            except Exception:
                return self.reply(503, {"error": "Agent execution failed; inspect local job history"})
    return Handler


def serve(*, database, protocol, registry, changed, token, port=8899,
          evidence_dir=None, trusted_sha=None):
    if not isinstance(token, str) or len(token) < 32:
        raise ValueError("Set a random local token at least 32 characters long")
    if not isinstance(port, int) or not 1024 <= port <= 65535:
        raise ValueError("Invalid local port")
    if not changed or len(changed) > 100:
        raise ValueError("Explicit changed files required")
    history = AgentHistory(database)
    server = HTTPServer(
        ("127.0.0.1", port),
        make_handler(history, token, str(protocol), str(registry), changed, evidence_dir, trusted_sha))
    try:
        print("HealthQualify local agent dashboard: http://127.0.0.1:" + str(port))
        server.serve_forever()
    finally:
        server.server_close()
        history.close()


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Single-user loopback-only synthetic agent dashboard")
    p.add_argument("--db", default=".healthqualify/agents.db")
    p.add_argument("--protocol", default="examples/synthetic_lis_v3/protocol.json")
    p.add_argument("--registry", default="examples/agents/dependencies.json")
    p.add_argument("--changed", nargs="+", default=["healthqualify/healthcare.py"])
    p.add_argument("--port", type=int, default=8899)
    args = p.parse_args(argv)
    token = os.environ.get("HEALTHQUALIFY_AGENT_TOKEN", "")
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    serve(database=args.db, protocol=args.protocol, registry=args.registry,
          changed=args.changed, token=token, port=args.port)


if __name__ == "__main__":
    main()
