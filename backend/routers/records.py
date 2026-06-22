"""NOL record CRUD, stats, and Excel export endpoints."""
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .. import storage, excel_export
from ..models import NOLRecord

router = APIRouter(prefix="/api", tags=["records"])


@router.get("/stats")
def get_stats():
    return storage.stats()


@router.get("/records")
def list_records():
    return storage.list_records()


@router.get("/records/export.xlsx")
def export_excel():
    """Build the tracker spreadsheet from current records and return it."""
    records = storage.list_records()
    data = excel_export.build_workbook(records)
    filename = f"NOL_Records_{datetime.now():%Y-%m-%d}.xlsx"
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/records/{record_id}")
def get_record(record_id: str):
    record = storage.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record


@router.post("/records")
def create_record(record: NOLRecord):
    return storage.add_record(record.model_dump())


@router.put("/records/{record_id}")
def update_record(record_id: str, record: NOLRecord):
    updated = storage.update_record(record_id, record.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found.")
    return updated


@router.delete("/records/{record_id}")
def delete_record(record_id: str):
    if not storage.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Record not found.")
    return {"deleted": True}
