"""Security and healthcare connector regression tests (synthetic only)."""
import base64
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from healthqualify.security import IdentityStore, AuthenticationError
from healthqualify.fhir_secure import assert_target, fetch_fhir, TransportDenied
from healthqualify.hl7_mllp import pack_mllp, unpack_mllp, analyze_message, MLLPError
from healthqualify.dicom_device import inspect_equipment_snapshot, DicomInspectionError, inspect_dicom_file
from healthqualify.secure_vault import encrypt_evidence, decrypt_evidence, sign_manifest, verify_manifest

class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.auth=IdentityStore(str(Path(self.tmp.name)/"auth.db"))
    def tearDown(self):
        self.auth.close()
        self.tmp.cleanup()

    def test_roles_and_sessions(self):
        self.auth.bootstrap("root_admin","long-admin-passphrase!")
        with self.assertRaises(AuthenticationError):
            self.auth.bootstrap("another_admin","very-secure-passphrase")
        with self.assertRaises(AuthenticationError):
            self.auth.login("root_admin","bad-password")
        admin_token=self.auth.login("root_admin","long-admin-passphrase!")
        admin=self.auth.authenticate(admin_token)
        self.auth.authorize(admin,"users")
        self.auth.create_user(admin,"clinical_qa","another-long-passphrase","qa")
        self.auth.create_user(admin,"user_view","another-long-passphrase","viewer")
        qa=self.auth.authenticate(self.auth.login("clinical_qa","another-long-passphrase"))
        self.auth.authorize(qa,"baseline")
        with self.assertRaises(AuthenticationError):
            self.auth.authorize(qa,"execute")
        viewer=self.auth.authenticate(self.auth.login("user_view","another-long-passphrase"))
        self.auth.authorize(viewer,"read")
        with self.assertRaises(AuthenticationError):
            self.auth.authorize(viewer,"write")
        self.auth.logout(admin_token)
        with self.assertRaises(AuthenticationError):
            self.auth.authenticate(admin_token)

    def test_session_expiry(self):
        self.auth.bootstrap("root_admin","long-admin-passphrase!")
        token=self.auth.login("root_admin","long-admin-passphrase!")
        self.auth.conn.execute("UPDATE hq_sessions SET expires=0")
        self.auth.conn.commit()
        with self.assertRaises(AuthenticationError):
            self.auth.authenticate(token)

class InteroperabilityTests(unittest.TestCase):
    def test_fhir_requires_https_allowlisted_origin(self):
        target="https://fhir.example.org/fhir/Observation/123"
        self.assertTrue(assert_target(target,"https://fhir.example.org"))
        for invalid in ("http://fhir.example.org/fhir/Observation/123",
                        "https://evil.example.org/fhir/Observation/123",
                        "https://fhir.example.org/private",
                        "https://fhir.example.org/fhir/../secret",
                        "https://127.0.0.1/fhir/Observation/123"):
            with self.subTest(invalid=invalid),self.assertRaises(TransportDenied):
                assert_target(invalid,"https://fhir.example.org")
        with self.assertRaises(TransportDenied):
            fetch_fhir(target,approved_origin="https://fhir.example.org",bearer_token="sample-secret-token",consent=False)

    def test_hl7_mllp_bounded(self):
        message="MSH|^~\\&|LIS|LAB|EHR|HOSP|20261114||ORU^R01|MSG|P|2.5\rPID|1||SYNTHETIC"
        framed=pack_mllp(message)
        self.assertEqual(unpack_mllp(framed),message)
        self.assertTrue(analyze_message(framed)["qualification_approved"] is False)
        with self.assertRaises(MLLPError):
            unpack_mllp(framed[:-1])
        with self.assertRaises(MLLPError):
            pack_mllp("NO-MSH")

    def test_equipment_passive(self):
        sample={"device_id":"SIM-1","software_version":"1.2","status":"ready","timestamp_utc":"2026-11-14"}
        with self.assertRaises(ValueError):
            inspect_equipment_snapshot(sample)
        result=inspect_equipment_snapshot(sample,authorized=True)
        self.assertFalse(result["device_command_sent"])
        self.assertFalse(result["qualification_approved"])

    def test_dicom_requires_explicit_synthetic_consent(self):
        with self.assertRaises(DicomInspectionError):
            inspect_dicom_file("irrelevant-file.dcm",synthetic_only=False)

class ProtectedEvidenceTests(unittest.TestCase):
    def test_encryption_and_signature_are_bound_and_tamper_evident(self):
        key=os.urandom(32)
        ciphertext=encrypt_evidence(b"synthetic-only-record",key,"RUN-1")
        self.assertNotIn(b"synthetic-only-record",ciphertext)
        self.assertEqual(decrypt_evidence(ciphertext,key,"RUN-1"),b"synthetic-only-record")
        with self.assertRaises((ValueError,Exception)):
            decrypt_evidence(ciphertext,key,"RUN-2")
        receipt=sign_manifest(b"manifest-v1",os.urandom(32))
        pub=base64.b64decode(receipt["public_key"])
        self.assertTrue(verify_manifest(b"manifest-v1",receipt,pub))
        self.assertFalse(verify_manifest(b"manifest-v2",receipt,pub))
        self.assertFalse(verify_manifest(b"manifest-v1",receipt,os.urandom(32)))

if __name__=="__main__":
    unittest.main()
