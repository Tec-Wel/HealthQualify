"""Attestation controls: password re-verification, role limits, author separation."""
import os
import json
import tempfile
import unittest
from pathlib import Path

from healthqualify.workspace import Workspace
from healthqualify.security import IdentityStore, AuthenticationError
from healthqualify.attestations import attest_protocol

EXAMPLE=Path(__file__).resolve().parents[1]/"examples"/"synthetic_lis_v2"/"protocol.json"

class AttestationTests(unittest.TestCase):
    def test_fresh_credentials_role_and_protocol_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            path=str(Path(temp)/"store.db")
            work=Workspace(path)
            ids=IdentityStore(path)
            ids.bootstrap("admin_001","admin-secret-passphrase")
            root=ids.authenticate(ids.login("admin_001","admin-secret-passphrase"))
            ids.create_user(root,"author_001","author-secret-passphrase","validator")
            ids.create_user(root,"qa_001","qa-secret-passphrase","qa")
            ids.close()
            system=work.add_system("Synthetic LIS","Test only","author_001")
            doc=json.loads(EXAMPLE.read_text())
            doc["system"]["id"]=system["id"]
            protocol=work.draft_protocol(system["id"],doc,"author_001")
            work.baseline(protocol["id"],"qa_001","Engineering review only")
            key=os.urandom(32)
            with self.assertRaises(AuthenticationError):
                attest_protocol(path,"author_001","author-secret-passphrase",
                                protocol["id"],"REVIEWED","review note",key)
            with self.assertRaises(AuthenticationError):
                attest_protocol(path,"qa_001","wrong-password",protocol["id"],"REVIEWED","review",key)
            receipt=attest_protocol(path,"qa_001","qa-secret-passphrase",
                                    protocol["id"],"REVIEWED","Engineering review",key)
            self.assertEqual(receipt["statement"]["protocol_digest"],protocol["digest"])
            self.assertFalse(receipt["regulatory_esignature"])
            count=work.conn.execute("SELECT COUNT(*) FROM hq_review_attestations").fetchone()[0]
            self.assertEqual(count,1)
            work.close()

if __name__=="__main__":
    unittest.main()
