"""Read-only local REST JSON test adapter for synthetic interoperability tests.

Never uses production URLs, writes requests, redirects, query parameters, or
uncensored response values in a qualification result. Does not assert clinical
FHIR conformance or regulatory validation.
"""
from __future__ import annotations
import json
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from .healthcare import value_at_path

class RedirectDenied(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Redirects forbidden")

def check_local_json(url: str, field_path: str, expected, *,
                     authorized: bool = False, max_bytes: int = 262144,
                     timeout: int = 4) -> dict:
    if authorized is not True:
        raise ValueError("Explicit test authorization required")
    if not isinstance(url,str) or len(url)>300:
        raise ValueError("Bounded synthetic URL required")
    parsed=urlsplit(url)
    if (parsed.scheme!="http" or parsed.hostname!="127.0.0.1" or
        not parsed.port or parsed.port<1 or parsed.port>65535 or
        parsed.username or parsed.password or parsed.query or parsed.fragment or
        not parsed.path.startswith("/test/") or ".." in parsed.path):
        raise ValueError("Only loopback synthetic /test/ endpoints permitted")
    if type(timeout) is not int or not 1<=timeout<=8 or type(max_bytes) is not int or not 1<=max_bytes<=262144:
        raise ValueError("Invalid network bounds")
    req=Request(url,headers={"Accept":"application/json","User-Agent":"HealthQualify-LocalREST/0.6"},
                method="GET")
    with build_opener(RedirectDenied).open(req,timeout=timeout) as response:
        if response.status!=200:
            return {"status":"ERROR","reason":"NON_200","qualification_approved":False}
        body=response.read(max_bytes+1)
    if len(body)>max_bytes:
        raise ValueError("Response exceeds safe size")
    data=json.loads(body)
    observed=value_at_path(data,field_path)
    passed=type(observed) is type(expected) and observed==expected
    return {"status":"PASS" if passed else "FAIL","check":"json_field_equals",
            "field":field_path,"observations_redacted":True,
            "qualification_approved":False,
            "notice":"Synthetic read-only REST assertion; not clinical approval."}
