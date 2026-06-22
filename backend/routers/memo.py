"""Memo package endpoint — builds the MTA memo from a record and appends the
scanned NOL PDF, returning one properly-named file.
"""
import json

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from ..services import memo as memo_service

router = APIRouter(prefix="/api", tags=["memo"])


@router.post("/memo-defaults")
def memo_defaults(record: dict):
    """Return suggested memo fields for a record (for the app to pre-fill)."""
    return memo_service.memo_defaults(record)


@router.post("/memo")
async def generate_memo(
    record: str = Form(...),   # JSON string of the NOL record
    memo: str = Form(...),     # JSON string of the memo fields
    scan: UploadFile = File(None),  # the scanned NOL PDF to attach
):
    try:
        record_data = json.loads(record)
        memo_data = json.loads(memo)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid record or memo data.")

    scan_bytes = await scan.read() if scan else b""

    try:
        package = memo_service.build_package(record_data, memo_data, scan_bytes)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Could not build memo: {e}")

    filename = memo_service.build_filename(record_data, memo_data)
    return StreamingResponse(
        iter([package]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
