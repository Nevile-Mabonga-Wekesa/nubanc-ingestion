# contracts/api/v1/event_trace.py
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Literal, Optional

router = APIRouter(prefix="/v1/events", tags=["events"])

# === Schemas ===
class EventStage(BaseModel):
    stage: Literal[
        "ingestion", "normalization", "ledger_projection", "audit_projection", "replay"
    ]
    status: Literal["pending", "completed", "failed"]
    timestamp: str
    details: Optional[str] = None

class EventTraceResponse(BaseModel):
    event_id: str
    tenant_id: str
    stages: List[EventStage]
    overall_status: Literal["pending", "completed", "failed"]

# === Veteran-level helper ===
def get_event_trace(event_id: str, tenant_id: str) -> EventTraceResponse:
    """
    In a real system, query the database or ledger for event stages.
    Here we simulate with mock data.
    """
    now = datetime.now(timezone.utc).isoformat()
    stages = [
        EventStage(stage="ingestion", status="completed", timestamp=now),
        EventStage(stage="normalization", status="completed", timestamp=now),
        EventStage(stage="ledger_projection", status="completed", timestamp=now),
        EventStage(stage="audit_projection", status="completed", timestamp=now),
        EventStage(stage="replay", status="pending", timestamp=now),
    ]

    overall_status = "completed" if all(s.status == "completed" for s in stages) else "pending"

    return EventTraceResponse(
        event_id=event_id,
        tenant_id=tenant_id,
        stages=stages,
        overall_status=overall_status,
    )

# === Endpoint ===
@router.get("/{event_id}/trace", response_model=EventTraceResponse)
def trace_event(event_id: str, x_tenant_id: str = Header(...)):
    """
    Return full event lineage for a given event ID.
    Multi-tenant aware.
    """
    try:
        trace = get_event_trace(event_id, x_tenant_id)
        return trace
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
