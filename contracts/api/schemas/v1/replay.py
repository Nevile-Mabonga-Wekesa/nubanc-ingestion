from typing import Optional, Literal
from pydantic import BaseModel


class ReplayRequest(BaseModel):
    from_timestamp: Optional[str] = None
    to_timestamp: Optional[str] = None
    dry_run: bool = False


class ReplayResponse(BaseModel):
    replay_id: str
    events_scanned: int
    events_replayed: int
    status: Literal["completed", "failed"]
    started_at: str
    completed_at: str
