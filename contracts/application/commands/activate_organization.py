from dataclasses import dataclass
from uuid import UUID

@dataclass
class ActivateOrganizationCommand:
    organization_id: UUID
    activated_by: str  # user_id (string or UUID)
