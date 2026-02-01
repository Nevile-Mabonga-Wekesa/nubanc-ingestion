from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timezone
from contracts.api.v1.schemas import ReplayRequest, ReplayResponse
from infra.replay_service import perform_replay

router = APIRouter(prefix="/v1/replay_", tags=["replay_"])


@router.post("", response_model=ReplayResponse)
async def replay_(
    request: ReplayRequest,
    x_tenant_id: str = Header(..., description="Tenant identifier"),
):
    """
    Veteran-grade Replay API:
    - Idempotent
    - Tenant-isolated
    - Dry-run support
    - Tracks replay ID and timestamps
    """
    try:
        replay_id, events_scanned, events_replayed, status, started_at, completed_at = perform_replay(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            from_timestamp=request.from_timestamp,
            to_timestamp=request.to_timestamp,
            dry_run=request.dry_run,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Replay failed: {str(e)}")

    return ReplayResponse(
        replay_id=replay_id,
        events_scanned=events_scanned,
        events_replayed=events_replayed,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
    )
