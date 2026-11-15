"""Restricted network authorization for non-production interoperability checks.

Only exact preapproved HTTPS origins. Hostname pinning protects against arbitrary
URLs, but DOES NOT by itself eliminate DNS-rebinding or compromised DNS risk.
Requires trusted network controls for deployment.
"""
from __future__ import annotations
import ipaddress
import json
import re
import ssl
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, HTTPSHandler
from .healthcare import value_at_path

class TransportDenied(ValueError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise TransportDenied("Redirects are forbidden")

def assert_target(url: str, approved_origin: str, path_prefix="/fhir/"):
    if not isinstance(url,str) or not isinstance(approved_origin,str):
        raise TransportDenied("URL and approved origin required")
    u,p=urlsplit(url),urlsplit(approved_origin)
    if (u.scheme!="https" or p.scheme!="https" or u.username or u.password or u.fragment
        or u.query or p.username or p.password or p.fragment or p.query or p.path not in ("","/")
        or not u.hostname or not p.hostname or (u.scheme,u.hostname,u.port)!=(p.scheme,p.hostname,p.port)
        or not u.path.startswith(path_prefix) or ".." in u.path or len(url)>500):
        raise TransportDenied("Target must match approved HTTPS origin and FHIR path")
    try:
        if ipaddress.ip_address(u.hostname).is_private or ipaddress.ip_address(u.hostname).is_loopback:
            raise TransportDenied("Private network endpoints require a separately designed connector")
    except ValueError as e:
        if isinstance(e,TransportDenied):
            raise
    return True

def fetch_fhir(url: str, *, approved_origin: str, bearer_token: str,
               consent: bool, max_bytes: int=512_000) -> dict:
    """Read-only FHIR GET, opt-in token from secret manager/environment, no redirects."""
    if consent is not True:
        raise TransportDenied("Explicit site-level authorization required")
    assert_target(url,approved_origin)
    if not isinstance(bearer_token,str) or len(bearer_token)<12 or "\n" in bearer_token or "\r" in bearer_token:
        raise TransportDenied("Validated bearer token required")
    if max_bytes<1 or max_bytes>512_000:
        raise TransportDenied("Response size limit exceeded")
    req=Request(url,headers={"Accept":"application/fhir+json","Authorization":"Bearer "+bearer_token,
                              "User-Agent":"HealthQualify/0.4"},method="GET")
    opener=build_opener(NoRedirect,HTTPSHandler(context=ssl.create_default_context()))
    with opener.open(req,timeout=8) as res:
        if res.status!=200: raise TransportDenied("Unexpected HTTP status")
        content=res.read(max_bytes+1)
    if len(content)>max_bytes: raise TransportDenied("FHIR response exceeds configured limit")
    parsed=json.loads(content)
    if not isinstance(parsed,dict) or not isinstance(parsed.get("resourceType"),str):
        raise TransportDenied("FHIR JSON resourceType missing")
    return parsed

def assert_fhir_field(doc: dict, field: str, expected) -> dict:
    value=value_at_path(doc,field)
    passed=type(value) is type(expected) and value==expected
    # Do not serialize raw values into evidence by default; could contain PHI.
    return {"status":"PASS" if passed else "FAIL","field":field,
            "qualification_approved":False,"source":"read_only_fhir_assertion"}
