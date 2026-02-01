from pydantic import BaseModel
from typing import Literal


class IngestFailureResponse(BaseModel):
    event_id: str
    failure_code: str
    failure_stage: Literal[
        "ingestion",
        "validation",
        "ledger_projection",
        "audit_projection",
        "unknown",
    ]
    failure_reason: str
    first_occurred_at: str
    last_observed_at: str
    replay_count: int
    deterministic: bool
