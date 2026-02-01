from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from contracts.api.db.base import Base
import enum

class InviteStatus(str, enum.Enum):
    INVITED = "INVITED"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class OrgUserInvite(Base):
    __tablename__ = "org_user_invites"

    id = Column(String, primary_key=True)  # ULID
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    status = Column(Enum(InviteStatus), nullable=False)
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    invited_by = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
