"""Safe offline DICOM dataset inspection (requires pydicom).

Does not implement network C-STORE or storage SCP, read pixel arrays, or validate
diagnostic image quality. Only accepts explicitly supplied synthetic DICOM files.
"""
from __future__ import annotations
from pathlib import Path

class DicomInspectionError(ValueError):
    pass

def inspect_dicom_file(path: str | Path, *, synthetic_only: bool=False) -> dict:
    if synthetic_only is not True:
        raise DicomInspectionError("Explicit synthetic-data authorization required")
    source=Path(path)
    if not source.is_file() or source.is_symlink() or source.stat().st_size>8*1024*1024:
        raise DicomInspectionError("Expected bounded regular file")
    try:
        import pydicom
    except ImportError as exc:
        raise DicomInspectionError("Install pydicom to enable DICOM inspection") from exc
    try:
        ds=pydicom.dcmread(str(source),stop_before_pixels=True,force=False)
    except Exception as exc:
        raise DicomInspectionError("Could not parse DICOM file") from exc
    sop=getattr(ds,"SOPClassUID",None)
    modality=getattr(ds,"Modality",None)
    return {"format":"DICOM","metadata_parsed":True,
            "sop_class_present":bool(sop),"modality_present":bool(modality),
            "pixel_data_processed":False,
            "patient_identifiers_exported":False,
            "qualification_approved":False}

def inspect_equipment_snapshot(snapshot: dict, *, authorized: bool=False) -> dict:
    """Validate bounded passive simulator telemetry. Never issues commands."""
    if not authorized:
        raise ValueError("Explicit authorization required")
    if not isinstance(snapshot,dict) or len(str(snapshot))>10_000:
        raise ValueError("Bounded telemetry object required")
    required={"device_id","software_version","status","timestamp_utc"}
    if not required.issubset(snapshot) or snapshot["status"] not in ("ready","idle","fault"):
        raise ValueError("Telemetry fields missing or invalid")
    return {"checked":sorted(required),"status":"OBSERVED","device_command_sent":False,
            "operational_qualification":"NOT_ASSESSED","qualification_approved":False}
