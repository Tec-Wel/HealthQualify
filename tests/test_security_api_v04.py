"""Security, protected-export, and authenticated HTTP regression tests."""
import base64
import json
import os
import tempfile
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from healthqualify.workspace import Workspace
from healthqualify.security import IdentityStore
from healthqualify.secure_api import make_handler
from healthqualify.protected_export import protect_export, verify_export
from healthqualify.reports import export_run

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/"examples"/"synthetic_lis_v2"/"protocol.json"

class SecureAPITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.database=str(Path(self.tmp.name)/"store.db")
        initial=IdentityStore(self.database)
        initial.bootstrap("admin_root","admin-secret-long-passphrase")
        initial.close()
        self.ready=threading.Event()
        def server_thread():
            self.work=Workspace(self.database)
            self.identities=IdentityStore(self.database)
            self.http=HTTPServer(("127.0.0.1",0),make_handler(self.work,self.identities))
            self.base=f"http://127.0.0.1:{self.http.server_port}"
            self.ready.set()
            try:
                self.http.serve_forever()
            finally:
                self.http.server_close()
                self.identities.close()
                self.work.close()
        self.thread=threading.Thread(target=server_thread,daemon=True)
        self.thread.start()
        self.assertTrue(self.ready.wait(timeout=5))

    def tearDown(self):
        self.http.shutdown()
        self.thread.join(timeout=4)
        self.assertFalse(self.thread.is_alive())
        self.tmp.cleanup()

    def request(self, path, data=None, token=None):
        headers={}
        if token:headers["Authorization"]="Bearer "+token
        if data is not None:headers["Content-Type"]="application/json"
        req=Request(self.base+path, data=None if data is None else json.dumps(data).encode(),
                    headers=headers)
        try:
            with urlopen(req,timeout=3) as response:
                return response.status,json.loads(response.read())
        except HTTPError as exc:
            return exc.code,json.loads(exc.read())

    def test_token_roles_and_server_derived_identity(self):
        self.assertEqual(self.request("/systems")[0],403)
        self.assertEqual(self.request("/systems",{"name":"forged","owner":"admin_root"})[0],403)
        self.assertEqual(self.request("/login",{"username":"admin_root","password":"wrong"})[0],403)
        status,login=self.request("/login",{"username":"admin_root","password":"admin-secret-long-passphrase"})
        self.assertEqual(status,200)
        admin=login["access_token"]
        self.assertEqual(self.request("/users",{"username":"qa_user","password":"qa-user-long-passphrase",
                                                 "role":"qa"},admin)[0],201)
        self.assertEqual(self.request("/users",{"username":"view_user","password":"viewer-long-passphrase",
                                                 "role":"viewer"},admin)[0],201)
        status,data=self.request("/systems",{"name":"Synthetic LIS","intended_use":"Engineering test",
                                               "owner":"forged"},admin)
        self.assertEqual(status,201)
        self.assertEqual(data["owner"],"admin_root")
        status,viewer_login=self.request("/login",{"username":"view_user","password":"viewer-long-passphrase"})
        viewer=viewer_login["access_token"]
        self.assertEqual(self.request("/systems",token=viewer)[0],200)
        self.assertEqual(self.request("/systems",{"name":"x","intended_use":"y"},viewer)[0],403)
        self.assertEqual(self.request("/audit",token=viewer)[0],403)
        self.assertEqual(self.request("/logout",{},admin)[0],200)
        self.assertEqual(self.request("/systems",token=admin)[0],403)

class ProtectedExportTests(unittest.TestCase):
    def test_signed_encrypted_export_and_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            workspace=Workspace(root/"records.db")
            system=workspace.add_system("Synthetic LIS","Demo only","Author")
            doc=json.loads(EXAMPLE.read_text())
            doc["system"]["id"]=system["id"]
            draft=workspace.draft_protocol(system["id"],doc,"Author")
            workspace.baseline(draft["id"],"QA","Engineering reference only")
            run=workspace.execute(draft["id"],"Author")
            raw=root/"raw"
            export_run(workspace,run["id"],raw)
            private=os.urandom(32)
            seed=os.urandom(32)
            sealed=root/"sealed"
            output=protect_export(raw,sealed,private,seed)
            public=base64.b64decode(output["signature"]["public_key"])
            self.assertTrue(verify_export(sealed,public))
            self.assertNotIn(b"Synthetic LIS",(sealed/"run.json.enc").read_bytes())
            self.assertFalse(verify_export(sealed,os.urandom(32)))
            with (sealed/"run.json.enc").open("ab") as handle:
                handle.write(b"tamper")
            self.assertFalse(verify_export(sealed,public))
            workspace.close()

if __name__=="__main__":
    unittest.main()
