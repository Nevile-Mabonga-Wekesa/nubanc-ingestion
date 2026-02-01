from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ReplayRequest(BaseModel):
    entity_type: str
    entity_id: Optional[str] = None  # If None, replay all entities
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None
    dry_run: bool = False  # Does not mutate state if True


class ReplayResponse(BaseModel):
    replay_id: str
    events_scanned: int
    events_replayed: int
    status: str  # completed | failed
    started_at: datetime
    completed_at: datetime
