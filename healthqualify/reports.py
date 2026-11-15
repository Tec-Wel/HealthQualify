"""HTML/JSON technical evidence reports. Not approval or regulatory certification."""
from __future__ import annotations
import html
import json
from pathlib import Path
from .assurance import encode, digest
from .workspace import Workspace

def render_html(run: dict, deviations: list[dict]) -> str:
    result=run["results"]
    esc=lambda v:html.escape(str(v),quote=True)
    rows=[]
    for r in result["results"]:
        rows.append("<tr><td>"+esc(r["id"])+"</td><td>"+esc(r["phase"])+"</td><td>"+
                    esc(r["status"])+"</td><td>"+esc(", ".join(r["requirement_ids"]))+
                    "</td><td>"+esc(r["detail"])+"</td></tr>")
    gaps="".join("<li>"+esc(d["kind"])+" — "+esc(d.get("test_id") or d.get("id"))+
                 " ("+esc(d["status"])+")</li>" for d in deviations)
    summary=" · ".join(esc(k)+": "+esc(v) for k,v in result["summary"].items())
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>HealthQualify Technical Evidence</title><style>
body{font:16px system-ui,sans-serif;max-width:1050px;margin:auto;padding:32px;color:#172b36;background:#fafcfd}
header{border-bottom:3px solid #165c70;padding-bottom:12px}
small{color:#52616b}table{width:100%;border-collapse:collapse;margin-top:18px}
th,td{padding:10px;text-align:left;border-bottom:1px solid #bdcbd1}
.notice{background:#fff1dd;padding:14px;border-left:5px solid #ba6821}
</style></head><body><header><h1>HealthQualify — Technical Evidence</h1>
<small>Not a qualification approval or regulatory certification</small></header>
<h2>""" + esc(result["system"].get("id")) + """</h2>
<p><strong>Run ID:</strong> """ + esc(run["id"]) + """</p>
<p><strong>Recorded:</strong> """ + esc(run["created_at"]) + """</p>
<p><strong>Results:</strong> """ + summary + """</p>
<div class="notice">Draft/technical evidence only. Requires qualified human review before any regulated use.</div>
<h2>Execution results</h2>
<table><thead><tr><th>Test</th><th>Phase</th><th>Status</th><th>Requirements</th><th>Detail</th></tr></thead>
<tbody>""" + "".join(rows) + """</tbody></table>
<h2>Open or recorded deviations</h2><ul>""" + gaps + """</ul>
<footer><small>Generated from a recorded execution run. Evidence integrity and approval controls depend on the deployment.</small></footer>
</body></html>"""

def export_run(workspace: Workspace, run_id: str, destination: Path) -> dict:
    run=workspace.one("runs",run_id)
    deviations=[d for d in workspace.list("deviations") if d["run_id"]==run_id]
    if destination.exists():
        raise FileExistsError("Report directory already exists")
    destination.mkdir(parents=True)
    artifacts={
      "report.html":render_html(run,deviations).encode("utf-8"),
      "run.json":encode(run),
      "deviations.json":encode(deviations)
    }
    for filename,data in artifacts.items():
        (destination/filename).write_bytes(data)
    manifest={"schema":"0.3","sha256":{name:digest(data) for name,data in artifacts.items()},
              "warning":"Unsigned, locally generated technical evidence; not a protected regulated record."}
    (destination/"manifest.json").write_bytes(encode(manifest))
    return manifest
