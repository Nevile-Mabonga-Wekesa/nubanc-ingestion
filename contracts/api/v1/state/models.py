from typing import List, Optional, Dict, Literal
from pydantic import BaseModel
from datetime import datetime


ConfidenceLevel = Literal["high", "degraded", "unknown"]


class Confidence(BaseModel):
    level: ConfidenceLevel
    reasons: List[str]


class DerivedFrom(BaseModel):
    raw_events: int
    normalized_events: int
    failed_events: int


class StateResponse(BaseModel):
    entity_type: str
    entity_id: str

    state: Dict[str, object]
    state_version: str

    derived_from: DerivedFrom

    last_updated_at: datetime

    confidence: Confidence
    inconsistencies: List[str]

    replay_safe: bool
