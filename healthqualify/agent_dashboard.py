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
:root{font:15px/1.55 system-ui,-apple-system,"Segoe UI",Arial,sans-serif;color:#102B45;background:#F5F8FC;--border:#DAE7ED;--teal:#0C8579;--text:#102B45;--muted:#5F7383;--surface:#fff;--focus:#075B9A}
*{box-sizing:border-box}
body{max-width:1260px;margin:0 auto;padding:34px 28px 80px}
header{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:33px 36px;background:linear-gradient(120deg,#102B45,#184B5A);border-radius:22px;box-shadow:0 14px 38px #102b451d}
header h1{font-size:34px;font-weight:800;letter-spacing:-.045em;color:#fff;line-height:1.2}
header h1 span{color:#76E3D0!important}
header p{color:#CFDFE6!important;margin-bottom:0}
h1,h2,h3{line-height:1.28}
h2{font-size:20px;letter-spacing:-.02em;margin:0 0 12px}
h3{font-weight:750}
small,.muted{color:var(--muted)}
header .pill{background:#245465;color:#A4F1E1;border:1px solid #448780}
.pill{border-radius:999px;padding:8px 13px;font-size:11px;letter-spacing:.055em;font-weight:800;white-space:nowrap}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:28px;margin-top:22px;box-shadow:0 8px 25px #0f27430b}
.panel>p:first-of-type{margin:0 0 18px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.agent{border:1px solid var(--border);border-radius:14px;padding:22px;background:#FAFCFE;display:flex;flex-direction:column;transition:border-color .15s,box-shadow .15s}
.agent:hover{border-color:#3EA998;box-shadow:0 10px 25px #0d776b12}
.agent h3{margin:0 0 8px;font-size:17px}
.agent p{color:#55697A;min-height:54px;margin:0 0 18px;flex:1;font-size:14px}
button{background:var(--teal);border:1px solid var(--teal);color:white;padding:11px 18px;border-radius:9px;cursor:pointer;font:inherit;font-size:14px;font-weight:750;transition:background .15s}
button:hover{background:#086B61}
button:focus-visible,input:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
button:disabled{opacity:.55;cursor:wait}
input[type=password]{padding:12px 14px;border:1px solid #B6C8D1;border-radius:9px;width:min(420px,100%);font:inherit}
input[type=checkbox]{accent-color:var(--teal);width:18px;height:18px;vertical-align:middle}
label{display:inline-flex;align-items:center;gap:9px;max-width:100%;margin-top:8px;color:#365364}
#result{white-space:pre-wrap;overflow-wrap:anywhere;max-height:530px;overflow:auto;background:#0D253B;color:#CFEDE9;padding:22px;border-radius:12px;border:1px solid #174C5A;font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace}
table{border-collapse:collapse;width:100%;font-size:13px}
td,th{padding:13px;text-align:left;border-bottom:1px solid #E1EAF0;overflow-wrap:anywhere}
th{background:#F0F7F8;color:#335768;font-size:12px}
.notice{padding:16px 19px;background:#FFF7E8;border-left:4px solid #C68C32;border-radius:9px;margin-top:20px;color:#604A20}
@media(max-width:680px){body{padding:16px 12px 48px}header{display:block;padding:24px}header h1{font-size:27px}.pill{display:inline-block;margin-top:14px}.panel{padding:19px}.grid{grid-template-columns:1fr}table{display:block;overflow:auto}input[type=password]{margin-bottom:10px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style></head><body>
<header><div><h1>HealthQualify <span style="color:#0d766b">AI Agents</span></h1><p class="muted">Five offline qualification investigators · synthetic developer alpha</p></div><div class="pill">LOCAL · DRAFT ONLY</div></header>
<div class="notice"><strong>Not a regulated approval system.</strong> Findings are advisory, model explanations are unverified, and QA release authorization is not supported.</div>
<section class="panel"><h2>Local access</h2><p>Enter the token configured for this workstation. It is kept in this page's memory only.</p>
<input id="token" type="password" autocomplete="off" placeholder="Local dashboard token"> <button onclick="refresh()">Load history</button>
<p class="muted">Default: deterministic analysis, with no model or network call.</p><label><input id="useollama" type="checkbox" style="width:auto"> Request optional local Qwen explanation (requires server --allow-ollama)</label></section>
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
 try{const result=await request("/api/run",{agent,use_ollama:document.querySelector("#useollama").checked});
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


def make_handler(history, token, protocol, registry, changed, evidence_dir=None, trusted_sha=None, allow_ollama=False):
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
                if not isinstance(payload, dict) or set(payload) != {"agent", "use_ollama"}:
                    raise ValueError("Only agent and use_ollama are accepted")
                use_ollama = payload["use_ollama"]
                if type(use_ollama) is not bool or (use_ollama and not allow_ollama):
                    raise ValueError("Local Ollama is disabled by server policy")
                agent = payload["agent"]
                if agent != "all" and agent not in AGENTS:
                    raise ValueError("Unknown agent")
                kw = {"changed_files": changed, "registry_path": registry,
                      "evidence_dir": evidence_dir, "trusted_manifest_sha256": trusted_sha,
                      "use_ollama": use_ollama}
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
          evidence_dir=None, trusted_sha=None, allow_ollama=False):
    if not isinstance(token, str) or len(token) < 32:
        raise ValueError("Set a random local token at least 32 characters long")
    if not isinstance(port, int) or not 1024 <= port <= 65535:
        raise ValueError("Invalid local port")
    if not changed or len(changed) > 100:
        raise ValueError("Explicit changed files required")
    history = AgentHistory(database)
    server = HTTPServer(
        ("127.0.0.1", port),
        make_handler(history, token, str(protocol), str(registry), changed, evidence_dir, trusted_sha, allow_ollama))
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
    p.add_argument("--allow-ollama", action="store_true", help="Allow explicit per-request local Ollama explanations")
    args = p.parse_args(argv)
    token = os.environ.get("HEALTHQUALIFY_AGENT_TOKEN", "")
    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    serve(database=args.db, protocol=args.protocol, registry=args.registry,
          changed=args.changed, token=token, port=args.port, allow_ollama=args.allow_ollama)


if __name__ == "__main__":
    main()
