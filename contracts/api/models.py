# models.py
from pydantic import BaseModel
from typing import Literal

class CreateOrgRequest(BaseModel):
    name: str
    entity_type: Literal["BANK", "FINTECH", "SME", "AUDITOR" "LENDERS"]
    country: str

class CreateOrgResponse(BaseModel):
    org_id: str
    status: str
