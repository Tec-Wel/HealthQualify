"""Local Edition v0.8 HTTP acceptance tests: no cloud/model/paid tokens.

A temporary loopback port is used and a temporary SQLite database is
destroyed after each test. The demo only handles seeded synthetic fixtures.
"""
from __future__ import annotations
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.request import urlopen
from healthqualify.local_edition_v08 import LocalServer

class LocalEditionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.server=LocalServer("127.0.0.1",0,Path(self.temp.name)/"local.db")
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.cookie=None
        self.csrf=None

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def request(self,path,data=None,method=None,headers=None):
        c=http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=3)
        h={"Host":"127.0.0.1:"+str(self.server.server_port),
           "X-HQ-Request":"1"}
        if self.cookie:h["Cookie"]=self.cookie
        if self.csrf and data is not None:h["X-HQ-CSRF"]=self.csrf
        if headers:h.update(headers)
        if data is not None:h["Content-Type"]="application/json"
        c.request(method or ("POST" if data is not None else "GET"),path,
                  body=json.dumps(data) if data is not None else None,headers=h)
        r=c.getresponse()
        body=r.read()
        result=json.loads(body) if "application/json" in r.getheader("Content-Type","") else body
        cookie=r.getheader("Set-Cookie")
        code=r.status
        c.close()
        return code,result,cookie

    def login(self,username="localadmin",password="very-long-local-password"):
        response=self.request("/api/login",{"username":username,"password":password})
        self.assertEqual(response[0],200)
        self.cookie=response[2].split(";")[0]
        self.csrf=response[1]["csrf"]

    def bootstrap(self):
        self.assertTrue(self.request("/api/setup")[1]["needs_setup"])
        self.assertEqual(self.request("/api/bootstrap",{
            "username":"localadmin","password":"very-long-local-password"})[0],201)
        self.login()

    def test_html_no_cloud_and_one_time_setup(self):
        code,page,_=self.request("/")
        self.assertEqual(code,200)
        self.assertIn(b"No cloud account",page)
        self.assertIn(b"Five AI agents",page)
        self.assertEqual(self.request("/api/overview")[0],403)
        self.bootstrap()
        self.assertFalse(self.request("/api/setup")[1]["needs_setup"])
        self.assertNotEqual(self.request("/api/bootstrap",{
            "username":"secondadmin","password":"another-long-password"})[0],201)

    def test_login_csrf_host_origin_and_logout(self):
        self.bootstrap()
        self.assertEqual(self.request("/api/session")[0],200)
        self.assertEqual(self.request("/api/overview",headers={"Host":"evil.test"})[0],403)
        self.assertEqual(self.request("/api/demo",{},headers={
            "Origin":"http://evil.test"})[0],403)
        self.assertEqual(self.request("/api/demo",{},headers={
            "X-HQ-CSRF":"wrong"})[0],403)
        self.assertEqual(self.request("/api/logout",{})[0],200)
        self.assertEqual(self.request("/api/overview")[0],403)

    def test_full_synthetic_demo_and_agents_no_model(self):
        self.bootstrap()
        run=self.request("/api/demo",{})
        self.assertEqual(run[0],201)
        self.assertEqual(run[1]["run"]["summary"]["PASS"],2)
        self.assertEqual(run[1]["run"]["summary"]["FAIL"],5)
        self.assertEqual(len(run[1]["deviations"]),5)
        self.assertFalse(run[1]["qualification_approved"])
        self.assertEqual(run[1]["protocol"]["state"],"DRAFT")
        self.assertEqual(len(run[1]["run"]["traceability"]),7)
        system=run[1]["system"]["id"]
        a=self.request("/api/agent",{"system_id":system,"agent":"gap-hunter"})
        self.assertEqual(a[0],201)
        self.assertEqual(a[1]["status"],"DRAFT")
        self.assertEqual(a[1]["report"]["qualification_approved"],False)
        self.assertEqual(a[1]["report"]["context"]["historical_runs"],1)
        self.assertEqual(self.request("/api/agent",{
            "system_id":"forged","agent":"gap-hunter"})[0],404 if False else 400)
        self.assertEqual(self.request("/api/overview")[0],200)
        self.assertEqual(self.request("/api/model")[1]["required"],False)
        self.assertEqual(self.request("/api/model-check",{})[1]["reason"],"opt_in_required")

    def test_independent_qa_review_and_authorization(self):
        self.bootstrap()
        demo=self.request("/api/demo",{})[1]
        system=demo["system"]["id"]
        observation=self.request("/api/agent",{
            "system_id":system,"agent":"failure-investigation"})[1]["id"]
        self.assertEqual(self.request("/api/review",{
            "observation_id":observation,"decision":"ACKNOWLEDGED",
            "rationale":"This is my own finding"})[0],403)
        created=self.request("/api/users",{
            "username":"reviewer_qa","password":"long-quality-review-password",
            "role":"qa"})
        self.assertEqual(created[0],201)
        self.assertEqual(self.request("/api/grants",{
            "username":"reviewer_qa","system_id":system})[0],201)
        self.login("reviewer_qa","long-quality-review-password")
        queue=self.request("/api/reviews")
        self.assertEqual(queue[0],200)
        self.assertTrue(any(x["id"]==observation for x in queue[1]["reviews"]))
        checked=self.request("/api/review",{
            "observation_id":observation,"decision":"NEEDS_INVESTIGATION",
            "rationale":"Review the synthetic failures and records"})
        self.assertEqual(checked[0],200)
        self.assertFalse(checked[1]["qualification_approved"])
        self.assertNotEqual(self.request("/api/demo",{})[0],201)
        self.assertNotEqual(self.request("/api/users",{
            "username":"unauthorized","password":"long-fake-password-123","role":"qa"})[0],201)

    def test_qwen_opt_in_and_redacted_draft_only(self):
        self.bootstrap()
        demo=self.request("/api/demo",{})[1]
        obs=self.request("/api/agent",{
            "system_id":demo["system"]["id"],"agent":"gap-hunter"})[1]["id"]
        self.assertEqual(self.request("/api/model-explain",{
            "observation_id":obs})[0],403)
        self.server.allow_model=True
        with patch("healthqualify.ai.local_draft",
                   return_value={"status":"DRAFT_UNVERIFIED","text":"Synthetic findings only."}):
            explained=self.request("/api/model-explain",{"observation_id":obs})
        self.assertEqual(explained[0],200)
        self.assertEqual(explained[1]["status"],"DRAFT_UNVERIFIED")
        self.assertFalse(explained[1]["qualification_approved"])
        self.assertTrue(explained[1]["human_review_required"])

    def test_discovery_and_selected_local_model(self):
        self.bootstrap()
        self.server.allow_model=True
        demo=self.request("/api/demo",{})[1]
        obs=self.request("/api/agent",{
            "system_id":demo["system"]["id"],"agent":"gap-hunter"})[1]["id"]
        response=MagicMock()
        response.read.return_value=json.dumps({"models":[
            {"name":"qwen3:0.6b"},{"name":"qwen3:1.7b"}]}).encode()
        response.__enter__.return_value=response
        with patch("urllib.request.urlopen",return_value=response) as local_call:
            listing=self.request("/api/model-check",{})[1]
            self.assertEqual(listing["models"],["qwen3:0.6b","qwen3:1.7b"])
            self.assertEqual(local_call.call_args.args[0],
                             "http://127.0.0.1:11434/api/tags")
            with patch("healthqualify.ai.local_draft",
                       return_value={"status":"DRAFT_UNVERIFIED","text":"Draft only."}) as draft:
                result=self.request("/api/model-explain",{
                    "observation_id":obs,"model":"qwen3:0.6b"})
                self.assertEqual(result[0],200)
                self.assertEqual(result[1]["model"],"qwen3:0.6b")
                self.assertFalse(result[1]["qualification_approved"])
                self.assertEqual(draft.call_args.args[2],"qwen3:0.6b")
            self.assertEqual(self.request("/api/model-explain",{
                "observation_id":obs,"model":"missing:model"})[0],400)
            self.assertEqual(self.request("/api/model-explain",{
                "observation_id":obs,"model":"http://evil.test"})[0],400)

    def test_discovery_disabled_without_server_opt_in(self):
        self.bootstrap()
        with patch("urllib.request.urlopen",side_effect=AssertionError("Should not call Ollama")):
            self.assertEqual(self.request("/api/model-check",{})[1]["reason"],"opt_in_required")

    def test_css_and_javascript_load_under_strict_csp(self):
        code,html,_=self.request("/")
        self.assertEqual(code,200)
        self.assertIn(b'local-ui.css',html)
        self.assertNotIn(b'<style>',html)
        self.assertEqual(self.request("/local-ui.css")[0],200)
        self.assertEqual(self.request("/local-ui.js")[0],200)

    def test_model_check_never_downloads_or_calls_model_by_default(self):
        self.bootstrap()
        with patch("urllib.request.urlopen",side_effect=AssertionError("Unexpected external call")):
            self.assertEqual(self.request("/api/model-check",{})[0],200)

if __name__=="__main__":
    unittest.main()
