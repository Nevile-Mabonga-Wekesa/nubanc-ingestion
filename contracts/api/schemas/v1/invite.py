# contracts/api/schemas/v1/invite.py
from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime


class OrgRole(str, Enum):
    ADMIN = "ADMIN"
    CREDIT_OFFICER = "CREDIT_OFFICER"
    RISK_MANAGER = "RISK_MANAGER"
    AUDITOR = "AUDITOR"


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: OrgRole


class InviteUserResponse(BaseModel):
    invite_id: str
    status: str
    expires_at: datetime
