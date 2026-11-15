"""Provider-neutral, draft-only AI abstraction. No remote calls by default."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .ai import ROLES, local_draft

@dataclass(frozen=True)
class Draft:
    provider: str
    role: str
    text: str
    status: str = "DRAFT_UNVERIFIED"
    evidence: bool = False
    approved: bool = False

class DraftProvider(Protocol):
    def suggest(self, role: str, input_text: str) -> Draft: ...

class DisabledProvider:
    def suggest(self, role, input_text):
        raise RuntimeError("AI disabled by default")

class LocalOllama:
    def __init__(self, model, consent=False):
        self.model=model
        self.consent=consent
    def suggest(self, role, input_text):
        result=local_draft(role,input_text,self.model,consent=self.consent)
        return Draft("local-ollama",role,result["text"])

def draft(provider: DraftProvider, role, input_text):
    if role not in ROLES or not isinstance(input_text,str) or not input_text.strip():
        raise ValueError("Valid specialist and bounded input required")
    if len(input_text)>12000:
        raise ValueError("Text length exceeded")
    result=provider.suggest(role,input_text)
    if not isinstance(result,Draft) or result.approved or result.evidence or result.status!="DRAFT_UNVERIFIED":
        raise ValueError("Provider attempted to declare execution evidence or approval")
    return result
