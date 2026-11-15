"""Bounded, synthetic-only loopback HTTP JSON assertion for developer alpha.

This module deliberately does not accept public hosts, redirects, writes, or
production data; it is not a general REST integration test framework.
"""
from __future__ import annotations

import ipaddress
import json
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPHandler
from urllib.error import URLError, HTTPError


class _NoRedirect(HTTPHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        raise ValueError("Redirects are not allowed")

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def check_local_json(url: str, field: str, expected, authorized: bool = False):
    if authorized is not True:
        raise ValueError("Synthetic-only read authorization required")
    parts = urlsplit(url)
    if parts.scheme != "http" or parts.hostname not in {"127.0.0.1", "::1"} or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Only explicit loopback HTTP URLs without credentials or query parameters are supported")
    if not isinstance(field, str) or not field or any(p in ("", "__proto__") for p in field.split(".")):
        raise ValueError("A nonempty dot-delimited JSON field is required")
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with build_opener(_NoRedirect()).open(req, timeout=3) as response:
            if response.status != 200:
                raise ValueError("Expected HTTP 200")
            if "application/json" not in response.headers.get("Content-Type", ""):
                raise ValueError("Expected JSON content type")
            body = response.read(65537)
            if len(body) > 65536:
                raise ValueError("Response exceeds 64 KiB")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ValueError("Local synthetic REST check failed") from exc
    obj = json.loads(body)
    observed = obj
    for key in field.split("."):
        if not isinstance(observed, dict) or key not in observed:
            return {"status": "FAIL", "field": field, "reason": "missing_field"}
        observed = observed[key]
    return {"status": "PASS" if observed == expected else "FAIL", "field": field,
            "expected": expected, "observed": observed}
