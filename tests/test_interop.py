"""Synthetic FHIR connector safety tests; no network connections required."""
import io
import json
import unittest
from unittest.mock import patch

from healthqualify.interop import fetch_local_fhir, check_local_fhir

class FakeResponse:
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,n):return json.dumps({"resourceType":"Observation","status":"final"}).encode()

class FakeOpener:
    def open(self,request,timeout):
        return FakeResponse()

class InteropTests(unittest.TestCase):
    def test_explicit_consent_and_host_validation(self):
        with self.assertRaises(ValueError):
            fetch_local_fhir("http://127.0.0.1:8000/fhir/Observation/1")
        for url in [
            "http://example.com/fhir/Observation/1",
            "http://127.0.0.1:8000/admin",
            "https://127.0.0.1:8000/fhir/Observation/1",
            "http://127.0.0.1:8000/fhir/Observation?identifier=abc",
            "http://localhost:8000/fhir/Observation/1",
        ]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                fetch_local_fhir(url,explicitly_authorized=True)

    def test_local_fhir_observation(self):
        with patch("healthqualify.interop.build_opener",return_value=FakeOpener()):
            url="http://127.0.0.1:8000/fhir/Observation/1"
            self.assertEqual(fetch_local_fhir(url,explicitly_authorized=True)["resourceType"],"Observation")
            passed=check_local_fhir(url,"status","final",authorized=True)
            failed=check_local_fhir(url,"status","amended",authorized=True)
            self.assertEqual(passed["status"],"PASS")
            self.assertEqual(failed["status"],"FAIL")
            self.assertFalse(passed["qualification_approved"])

if __name__=="__main__":
    unittest.main()
