from typing import Dict, Any
from pydantic import BaseModel


class CanonicalEvent(BaseModel):
    event_type: str
    tenant_id: str
    vendor: str
    vendor_version: str
    payload: Dict[str, Any]

class NormalizedEvent(BaseModel):
    event_id: str
    tenant_id: str
    upload_id: str
    normalization_version: str
    payload: Dict[str, Any]
