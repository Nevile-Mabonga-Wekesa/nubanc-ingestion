from pydantic import BaseModel
from typing import Optional, Dict, List
from enum import Enum

class FileType(str, Enum):
    statement = "statement"
    loan_book = "loan_book"
    csv = "csv"

class FileUploadSchema(BaseModel):
    file_type: FileType
    metadata: Optional[Dict] = {}

class FileStatusSchema(BaseModel):
    file_id: str
    status: str
    errors: Optional[List[Dict]] = []
