import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config import UPLOAD_DIR, settings
from ..database import get_db
from ..services.rag import ingest
router = APIRouter(prefix="/api/documents", tags=["documents"])
@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}: raise HTTPException(415, "Upload PDF, DOCX or TXT")
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not data: raise HTTPException(400, "File is empty")
    if len(data) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(413, "File too large")
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    path.write_bytes(data)
    try:
        count = ingest(path, db, display_name=(file.filename or path.name))
        return {"filename": file.filename, "chunks_indexed": count}
    except Exception as exc:
        db.rollback()
        raise HTTPException(400, f"Could not process document: {type(exc).__name__}")
    finally:
        path.unlink(missing_ok=True)
