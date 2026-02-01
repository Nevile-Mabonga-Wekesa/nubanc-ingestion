from typing import Optional, Literal
from pydantic import BaseModel


class ArtifactStatus(BaseModel):
    raw_event: bool
    ledger_entry: bool
    audit_entry: bool


class FailureInfo(BaseModel):
    code: str
    message: str


class IngestStatusResponse(BaseModel):
    event_id: str
    event_type: str
    status: Literal["accepted", "processed", "failed"]
    received_at: str
    last_updated_at: str
    environment: str
    artifacts: ArtifactStatus
    failure: Optional[FailureInfo] = None
