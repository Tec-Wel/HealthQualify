"""Source-linked regulatory catalog and explicit applicability decisions.

Not legal advice, a live regulatory interpretation engine, or proof of compliance.
All framework references are pointers, not redistributions of proprietary content.
"""
from __future__ import annotations
import difflib
import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

CATALOG={
    "us-part-11":{
       "name":"21 CFR Part 11", "kind":"regulation", "jurisdiction":"US",
       "source":"https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11",
       "scope":"Electronic records and signatures where applicable"},
    "fda-csa":{
       "name":"FDA Computer Software Assurance", "kind":"guidance", "jurisdiction":"US",
       "source":"https://www.fda.gov/regulatory-information/search-fda-guidance-documents/computer-software-assurance-production-and-quality-management-system-software",
       "scope":"Risk-based assurance for medical-device production and QMS software"},
    "eu-annex-11":{
       "name":"EU GMP Annex 11", "kind":"gmp-annex", "jurisdiction":"EU",
       "source":"https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en",
       "scope":"Computerised systems in GMP-regulated activities"},
    "eu-annex-15":{
       "name":"EU GMP Annex 15", "kind":"gmp-annex", "jurisdiction":"EU",
       "source":"https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en",
       "scope":"Qualification and validation in GMP manufacture"},
    "gamp5":{
       "name":"ISPE GAMP 5 (second edition)", "kind":"industry-guidance", "jurisdiction":"international",
       "source":"https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition",
       "scope":"Risk-based computerized-system assurance; licensed publication"},
    "iec62304":{
       "name":"IEC 62304", "kind":"standard", "jurisdiction":"international",
       "source":"https://webstore.iec.ch/",
       "scope":"Medical device software lifecycle, if applicable"}
}

def list_controls() -> list[dict]:
    return [{"id":id, **item} for id,item in CATALOG.items()]

def applicability(system: dict, decisions: dict[str,str]) -> dict:
    """Only user-provided applicability is ever recorded; UNKNOWN never means compliant."""
    if not isinstance(system,dict) or not system.get("intended_use"):
        raise ValueError("System intended use required")
    if not isinstance(decisions,dict) or not decisions:
        raise ValueError("At least one explicit framework decision required")
    allowed={"APPLICABLE","NOT_APPLICABLE","UNDETERMINED"}
    if any(k not in CATALOG or v not in allowed for k,v in decisions.items()):
        raise ValueError("Unsupported framework or decision")
    return {"intended_use":system["intended_use"],
            "assessments":[{"framework":key,"decision":status,"source":CATALOG[key]["source"],
                            "requires_authorized_review":True} for key,status in decisions.items()],
            "regulatory_approval":False,
            "warning":"Applicability supplied by reviewer; this tool does not determine legal obligations."}

def compare_text(old: str, new: str) -> dict:
    if not isinstance(old,str) or not isinstance(new,str) or len(old)>2_000_000 or len(new)>2_000_000:
        raise ValueError("Regulatory text must be bounded strings")
    old_lines=old.splitlines()
    new_lines=new.splitlines()
    lines=list(difflib.unified_diff(old_lines,new_lines,fromfile="old",tofile="new",lineterm=""))
    return {"changed":bool(lines),"unified_diff":"\n".join(lines),
            "legal_significance":"NOT_ASSESSED","human_review_required":bool(lines)}

def fetch_ecfr_section(title: int, date: str, part: int, section: str) -> str:
    """Explicit opt-in lookup at the official eCFR API; no model involved.

    URL is assembled from bounded numeric/section inputs and cannot target user hosts.
    """
    if type(title) is not int or not 1<=title<=50 or type(part) is not int or not 1<=part<=9999:
        raise ValueError("Invalid CFR title or part")
    import re
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",date or ""):
        raise ValueError("Date must be YYYY-MM-DD")
    if not re.fullmatch(r"[0-9]+\.[0-9A-Za-z-]+",section or ""):
        raise ValueError("Invalid CFR section")
    url=f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-{title}.xml?part={part}&section={section}"
    # Only the authoritative eCFR API is eligible; no redirects to other hosts.
    from urllib.request import HTTPRedirectHandler, build_opener
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):
            raise ValueError("eCFR redirect denied")
    with build_opener(NoRedirect).open(Request(url,headers={"User-Agent":"HealthQualify/0.3"}),timeout=8) as response:
        payload=response.read(2_000_001)
    if len(payload)>2_000_000:
        raise ValueError("Regulatory response exceeds limit")
    return payload.decode("utf-8")
