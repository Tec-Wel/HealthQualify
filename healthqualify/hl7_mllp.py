"""HL7 v2 MLLP bounded framing/decoding with no outbound device operations.

Receiving bytes or parsing a frame does not establish clinical or semantic
conformance; implement site-specific profiles and witnessed workflows separately.
"""
from __future__ import annotations

START=b"\x0b"
END=b"\x1c\x0d"
MAX_MESSAGE=256*1024

class MLLPError(ValueError):
    pass

def pack_mllp(message: str) -> bytes:
    """Create a transport frame for an explicitly authorized synthetic test."""
    if not isinstance(message,str) or not message.startswith("MSH|"):
        raise MLLPError("HL7 message must begin with MSH")
    payload=message.encode("utf-8")
    if len(payload)>MAX_MESSAGE or START in payload or b"\x1c" in payload:
        raise MLLPError("Oversized or invalid control bytes")
    return START+payload+END

def unpack_mllp(frame: bytes) -> str:
    if not isinstance(frame,bytes) or len(frame)>MAX_MESSAGE+3:
        raise MLLPError("Invalid frame size")
    if not frame.startswith(START) or not frame.endswith(END):
        raise MLLPError("MLLP start/end delimiters missing")
    payload=frame[1:-2]
    if START in payload or b"\x1c" in payload:
        raise MLLPError("Unexpected control delimiter in frame")
    try: decoded=payload.decode("utf-8")
    except UnicodeDecodeError as exc: raise MLLPError("Invalid UTF-8") from exc
    if not decoded.startswith("MSH|"):
        raise MLLPError("Not an HL7 message")
    return decoded

def analyze_message(frame: bytes) -> dict:
    from .healthcare import parse_hl7
    msg=unpack_mllp(frame)
    parsed=parse_hl7(msg)
    if "MSH" not in parsed:
        raise MLLPError("Message header missing")
    # Metadata only: no patient identifiers, observations, or raw payload returned.
    return {"status":"PARSED","segment_types":sorted(parsed),
            "segment_count":sum(len(values) for values in parsed.values()),
            "clinical_validity":"NOT_ASSESSED","qualification_approved":False}
