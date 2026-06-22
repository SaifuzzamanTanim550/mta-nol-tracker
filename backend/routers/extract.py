"""PDF extraction endpoint."""
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..services import openai_extract as extractor

router = APIRouter(prefix="/api", tags=["extract"])


@router.post("/extract")
async def extract(file: UploadFile = File(...)):
    """Accept an NOL PDF and return the extracted fields."""
    if file.content_type not in ("application/pdf", "application/octet-stream") \
            and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        fields = extractor.extract_fields_from_pdf(pdf_bytes)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"fields": fields}