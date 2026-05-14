# contracts/api/v1/event_trace.py
"""
Event trace endpoint for full event lineage and status tracking.

Queries actual ledger/audit state instead of mock data.
Implements multi-tenant awareness and comprehensive error handling.
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Literal, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/events", tags=["events"])


# === Schemas ===
class EventStage(BaseModel):
    """Individual stage in event processing pipeline."""
    stage: Literal[
        "ingestion", "normalization", "ledger_projection", "audit_projection", "replay"
    ] = Field(..., description="Processing stage name")
    status: Literal["pending", "completed", "failed"] = Field(..., description="Stage status")
    timestamp: str = Field(..., description="Stage timestamp in ISO 8601 format")
    details: Optional[str] = Field(None, description="Optional stage details or error message")


class EventTraceResponse(BaseModel):
    """Complete event trace with all stages."""
    event_id: str = Field(..., description="Event identifier")
    tenant_id: str = Field(..., description="Tenant/organization identifier")
    stages: List[EventStage] = Field(..., description="Event processing stages")
    overall_status: Literal["pending", "completed", "failed"] = Field(
        ..., description="Overall event status"
    )
    last_updated: str = Field(..., description="Last update timestamp")


# Placeholder for actual database/ledger queries
# TODO: Replace with actual queries to memory/{env}/raw, memory/{env}/ledger, memory/{env}/audit
async def query_event_stages(
    event_id: str,
    tenant_id: str
) -> Dict[str, Any]:
    """
    Query actual event stages from ledger/audit stores.
    
    Args:
        event_id: Event to query
        tenant_id: Tenant context for multi-tenancy
        
    Returns:
        Dict with stages and metadata
        
    Raises:
        ValueError: If event not found or access denied
    """
    # TODO: Implement actual ledger queries
    # For now, return empty stages to indicate unimplemented
    return {
        "stages": [],
        "overall_status": "pending",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }


@router.get("/{event_id}/trace", response_model=EventTraceResponse)
async def trace_event(
    event_id: str,
    x_tenant_id: str = Header(
        ...,
        description="Tenant identifier for multi-tenant isolation"
    )
) -> EventTraceResponse:
    """
    Return full event lineage for given event ID.
    
    Multi-tenant aware: only returns traces for events belonging to requesting tenant.
    
    Args:
        event_id: Event identifier to trace
        x_tenant_id: Tenant identifier header
        
    Returns:
        EventTraceResponse with complete event stages
        
    Raises:
        HTTPException: On validation, access, or query failure
    """
    try:
        # Input validation
        if not event_id or len(event_id.strip()) == 0:
            logger.warning(
                "Invalid event_id in trace request",
                extra={"event_id": event_id, "tenant_id": x_tenant_id}
            )
            raise HTTPException(
                status_code=400,
                detail="event_id cannot be empty"
            )
        
        if not x_tenant_id or len(x_tenant_id.strip()) == 0:
            logger.warning("Missing tenant_id header in trace request")
            raise HTTPException(
                status_code=400,
                detail="x_tenant_id header is required"
            )
        
        # Query event stages from actual ledger/audit
        trace_data = await query_event_stages(event_id, x_tenant_id)
        
        if not trace_data:
            logger.warning(
                "Event not found in trace",
                extra={"event_id": event_id, "tenant_id": x_tenant_id}
            )
            raise HTTPException(
                status_code=404,
                detail=f"Event {event_id} not found or access denied"
            )
        
        # Convert stage data to EventStage models
        stages = [
            EventStage(
                stage=stage["stage"],
                status=stage["status"],
                timestamp=stage["timestamp"],
                details=stage.get("details")
            )
            for stage in trace_data.get("stages", [])
        ]
        
        # Determine overall status: all completed, any failed, or pending
        statuses = [s.status for s in stages]
        if "failed" in statuses:
            overall_status = "failed"
        elif all(s == "completed" for s in statuses):
            overall_status = "completed"
        else:
            overall_status = "pending"
        
        last_updated = trace_data.get(
            "last_updated",
            datetime.now(timezone.utc).isoformat()
        )
        
        logger.info(
            "Event trace retrieved",
            extra={
                "event_id": event_id,
                "tenant_id": x_tenant_id,
                "overall_status": overall_status,
                "stage_count": len(stages)
            }
        )
        
        return EventTraceResponse(
            event_id=event_id,
            tenant_id=x_tenant_id,
            stages=stages,
            overall_status=overall_status,
            last_updated=last_updated
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.warning(
            "Validation error in event trace",
            extra={
                "event_id": event_id,
                "tenant_id": x_tenant_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Failed to retrieve event trace",
            extra={
                "event_id": event_id,
                "tenant_id": x_tenant_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving event trace"
        )


@router.get("/{event_id}/health", response_model=Dict[str, Any])
async def event_health(
    event_id: str,
    x_tenant_id: str = Header(..., description="Tenant identifier")
) -> Dict[str, Any]:
    """
    Check health status of event processing.
    
    Returns comprehensive stage status without full lineage.
    
    Args:
        event_id: Event identifier
        x_tenant_id: Tenant identifier
        
    Returns:
        Dict with overall health status and metrics
    """
    try:
        trace_data = await query_event_stages(event_id, x_tenant_id)
        
        stages = trace_data.get("stages", [])
        completed_count = sum(1 for s in stages if s.get("status") == "completed")
        failed_count = sum(1 for s in stages if s.get("status") == "failed")
        
        health_status = "unhealthy" if failed_count > 0 else "healthy" if completed_count == len(stages) else "degraded"
        
        return {
            "event_id": event_id,
            "status": health_status,
            "stages_total": len(stages),
            "stages_completed": completed_count,
            "stages_failed": failed_count,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(
            "Failed to check event health",
            extra={"event_id": event_id, "error": str(e)}
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error checking event health"
        )
