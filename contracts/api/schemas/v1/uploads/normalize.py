# contracts/api/schemas/v1/uploads/normalize.py
from pydantic import BaseModel, Field
from typing import List

class NormalizeRequest(BaseModel):
    event_ids: List[str] = Field(..., description="List of raw ingest event IDs to normalize")
    normalization_version: str = Field(..., description="Version of normalization logic")

class NormalizeResponse(BaseModel):
    status: str = Field(..., description="accepted if normalization queued")
    upload_id: str = Field(..., description="Upload ID corresponding to events")
    events_normalized: int = Field(..., description="Number of events normalized")
    normalized_event_ids: List[str] = Field(..., description="List of normalized event IDs")
