from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
import shutil
import os

from ..db import SessionLocal, FileRecord, FileStatus
from contracts.api.services.queue import push_to_queue
from enum import Enum

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = "./uploads/raw"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileType(str, Enum):
    statements= "statements"
    loan_books= "loan_books"
    csv= "csv"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
async def upload_file(file: UploadFile = File(...),
                      file_type: FileType = Form(...),
                      uploader: str = Form(...),
                      metadata: str = Form("{}"),
                      db: Session = Depends(get_db)):
    # Generate unique file ID
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save file to staging
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    record = FileRecord(
        file_id=file_id,
        file_type=file_type.value,
        uploader=uploader,
        metadata=metadata,
        status=FileStatus.queued
    )
    db.add(record)
    db.commit()

    # Push to normalization queue
    push_to_queue(file_id)

    return {"file_id": file_id, "status": "queued", "message": "File uploaded successfully"}


@router.get("/{file_id}")
def get_file_status(file_id: str, db: Session = Depends(get_db)):
    record = db.query(FileRecord).filter(FileRecord.file_id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "file_id": record.file_id,
        "status": record.status.value,
        "errors": record.errors
    }
