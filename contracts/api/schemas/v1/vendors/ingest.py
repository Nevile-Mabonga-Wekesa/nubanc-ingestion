from typing import List
from pydantic import BaseModel


class VendorIngestResponse(BaseModel):
    status: str  # "accepted"
    vendor: str
    events_emitted: int
    event_ids: List[str]
