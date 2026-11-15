"""Explicitly authorized, read-only FHIR test-environment connector.

The v0.3 connector is restricted to the local machine. It never writes data,
uses credentials, connects to production systems or accepts arbitrary URLs.
"""
from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from .healthcare import value_at_path, CheckError

class BlockRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ValueError("Redirect denied for read-only healthcare test connector")

def fetch_local_fhir(url: str, *, explicitly_authorized: bool = False) -> dict:
    if not explicitly_authorized:
        raise ValueError("Explicit authorization required for network test")
    if not isinstance(url,str) or len(url)>250:
        raise ValueError("URL must be bounded")
    parsed=urlsplit(url)
    if (parsed.scheme!="http" or parsed.hostname!="127.0.0.1"
            or not 1<= (parsed.port or 0) <=65535 or parsed.username or parsed.password
            or parsed.fragment or parsed.query or not parsed.path.startswith("/fhir/")):
        raise ValueError("Only loopback synthetic FHIR endpoints are supported")
    request=Request(url,headers={"Accept":"application/fhir+json","User-Agent":"HealthQualify-Test/0.3"})
    with build_opener(BlockRedirect).open(request,timeout=4) as response:
        if response.status!=200:
            raise ValueError("FHIR endpoint returned non-200 response")
        data=response.read(512001)
    if len(data)>512000:
        raise ValueError("FHIR fixture response exceeds 500KB limit")
    document=json.loads(data)
    if not isinstance(document,dict) or not isinstance(document.get("resourceType"),str):
        raise CheckError("Response is not a FHIR JSON resource object")
    return document

def check_local_fhir(url: str, path: str, expected, *, authorized: bool = False) -> dict:
    doc=fetch_local_fhir(url,explicitly_authorized=authorized)
    observed=value_at_path(doc,path)
    match=type(observed) is type(expected) and observed==expected
    return {"status":"PASS" if match else "FAIL","path":path,"actual":observed,
            "expected":expected,"qualification_approved":False,
            "warning":"Local synthetic interoperability check only; no clinical validation or approval."}
