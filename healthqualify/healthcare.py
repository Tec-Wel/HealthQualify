"""Healthcare-specific deterministic assertions for synthetic integration fixtures.

These checks interpret read-only JSON/HL7 strings. They never connect to clinical
systems, execute generated code, modify records, or evaluate actual patient data.
"""
from __future__ import annotations

from typing import Any


class CheckError(ValueError):
    """The test input cannot be interpreted; never record this as a pass."""


def parse_hl7(message: str) -> dict[str, list[list[str]]]:
    if not isinstance(message, str) or not message.startswith("MSH|"):
        raise CheckError("Synthetic HL7 message must start with MSH|")
    segments: dict[str, list[list[str]]] = {}
    for raw in message.replace("\\r", "\n").splitlines():
        if not raw.strip():
            continue
        fields = raw.split("|")
        if len(fields[0]) != 3 or not fields[0].isupper():
            raise CheckError("Invalid HL7 segment name")
        segments.setdefault(fields[0], []).append(fields)
    return segments


def value_at_path(value: Any, path: str) -> Any:
    if not isinstance(path, str) or not path or path.startswith("."):
        raise CheckError("Non-empty JSON field path required")
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            raise CheckError("FHIR path missing: " + part)
        current = current[part]
    return current


def observe(check: str, actual: Any, test: dict) -> tuple[bool, Any]:
    """Return whether a check met its sourced acceptance value, and observation.

    Paths and field identifiers are explicit, not generated Python/SQL expressions.
    """
    expected = test.get("expected")
    if check == "equals":
        return type(actual) is type(expected) and actual == expected, actual
    if check == "present":
        return actual is not None, actual
    if check == "hl7_field_equals":
        segs = parse_hl7(actual)
        segment = test.get("segment")
        index = test.get("field_index")
        if not isinstance(segment, str) or not isinstance(index, int) or index < 1:
            raise CheckError("segment and positive field_index required")
        if segment not in segs or len(segs[segment]) != 1:
            raise CheckError("Expected exactly one segment: " + segment)
        fields = segs[segment][0]
        if index >= len(fields):
            raise CheckError("HL7 field not present")
        found = fields[index]
        return found == expected, found
    if check == "fhir_field_equals":
        found = value_at_path(actual, test.get("path"))
        return type(found) is type(expected) and found == expected, found
    if check == "role_denied":
        if not isinstance(actual, dict) or not isinstance(actual.get("allowed"), bool):
            raise CheckError("Authorization fixture must contain boolean allowed")
        found = actual["allowed"]
        return found is False, found
    raise CheckError("Unsupported check type")
