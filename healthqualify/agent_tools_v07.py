"""Explicit read-only tool contract for scoped HealthQualify investigators.

No arbitrary SQL, filesystem browsing, network calls, Python execution or
modification of qualification records. All tools use authenticated system scope.
"""
from __future__ import annotations
from .agent_runtime_v07 import ScopedAgentRuntime

TOOL_NAMES=("system_summary","protocol_versions","requirement_index",
            "recent_runs","deviations","compare_latest_runs","agent_metrics")

class AgentToolbox:
    def __init__(self,runtime:ScopedAgentRuntime, token:str, system_id:str):
        self.runtime=runtime
        self.token=token
        self.system_id=system_id
        # Fail early on invalid/expired token or missing grant.
        runtime.system_context(token,system_id,limit=1)

    def call(self,name,*,limit=10):
        if name not in TOOL_NAMES:
            raise ValueError("Unknown or unsafe agent tool")
        if type(limit) is not int or not 1<=limit<=50:
            raise ValueError("Invalid bounded limit")
        context=self.runtime.system_context(self.token,self.system_id,limit=limit)
        if name=="system_summary":
            return {"system":context["system"],"scope":"REDACTED_METADATA_ONLY"}
        if name=="protocol_versions":
            return {"protocols":context["protocols"]}
        if name=="requirement_index":
            # Existing workspace stores v0.2 protocols. Return metadata only;
            # do not pass full acceptance or fixture data to a model.
            protocols=self.runtime.conn.execute(
                "SELECT id,payload FROM protocols WHERE system_id=? ORDER BY version DESC LIMIT 1",
                (self.system_id,)).fetchall()
            rows=[]
            for p in protocols:
                import json
                data=json.loads(p["payload"])
                for r in data.get("requirements",[]):
                    rows.append({"id":r["id"],"risk":r["risk"],
                                 "source_id":r.get("source_id"),
                                 "protocol_id":p["id"]})
            return {"requirements":rows,"raw_acceptance_values_exported":False}
        if name=="recent_runs":
            return {"runs":context["runs"]}
        if name=="deviations":
            return {"deviations":context["deviations"]}
        if name=="compare_latest_runs":
            return {"historical_findings":self.runtime.historical_findings(context),
                    "history_depth":len(context["runs"]),
                    "root_cause_established":False}
        return self.runtime.metrics(self.token,self.system_id)
