from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date

class Period(BaseModel):
    from_: date = Field(..., alias="from")
    to: date

class Source(BaseModel):
    provider: str
    method: str

class FileRef(BaseModel):
    file_name: str
    file_type: str
    checksum: str

class FinanceStatementSubmitted(BaseModel):
    statement_type: str
    period: Period
    source: Source
    files: List[FileRef]
    metadata: Optional[Dict[str, str]] = None
