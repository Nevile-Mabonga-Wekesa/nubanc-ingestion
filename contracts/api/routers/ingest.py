# contracts/api/routers/ingest.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field, validator
import ulid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/ingest", tags=["Ingest"])


class IngestRequest(BaseModel):
    """Request to create ingestion event."""
    upload_id: str = Field(..., min_length=1, description="Upload identifier")
    source_type: str = Field(..., min_length=1, description="Data source type")
    format: str = Field(..., min_length=1, description="Data format (csv, json, xml, etc)")

    @validator('source_type')
    def validate_source_type(cls, v):
        """Validate source type is known format."""
        allowed = {'csv', 'json', 'xml', 'parquet', 'avro'}
        if v.lower() not in allowed:
            raise ValueError(f'source_type must be one of {allowed}')
        return v.lower()

    @validator('format')
    def validate_format(cls, v):
        """Validate format specification."""
        if len(v) > 100:
            raise ValueError('format string too long')
        return v


class IngestResponse(BaseModel):
    """Response from ingestion event creation."""
    event_id: str = Field(..., description="Unique event identifier")
    status: str = Field(..., description="Current ingestion status")
    upload_id: str = Field(..., description="Associated upload ID")


# In-memory event store (TODO: replace with database)
_ingest_events = {}


@router.post("/", response_model=IngestResponse, status_code=201)
async def create_ingest_event(
    payload: IngestRequest,
    x_tenant_id: str = Header(..., description="Tenant identifier")
) -> IngestResponse:
    """
    Create ingestion event and queue for processing.
    
    Args:
        payload: Ingestion request with source details
        x_tenant_id: Tenant identifier header
        
    Returns:
        IngestResponse with event ID and initial status
        
    Raises:
        HTTPException: On validation or processing failure
    """
    try:
        # Generate deterministic event ID using ULID (sortable, distributed-safe)
        event_id = str(ulid.new())
        
        # Store event state (TODO: persist to database)
        event_record = {
            "event_id": event_id,
            "status": "PENDING",
            "upload_id": payload.upload_id,
            "source_type": payload.source_type,
            "format": payload.format,
            "tenant_id": x_tenant_id
        }
        _ingest_events[event_id] = event_record
        
        logger.info(
            "Ingest event created",
            extra={
                "event_id": event_id,
                "upload_id": payload.upload_id,
                "tenant_id": x_tenant_id
            }
        )
        
        return IngestResponse(
            event_id=event_id,
            status="PENDING",
            upload_id=payload.upload_id
        )
    except ValueError as e:
        logger.error(f"Validation error in ingest: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to create ingest event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error creating ingest event"
        )


@router.get("/{event_id}", response_model=IngestResponse)
async def get_ingest_event(
    event_id: str,
    x_tenant_id: str = Header(..., description="Tenant identifier")
) -> IngestResponse:
    """
    Fetch ingestion event status by ID.
    Validates event belongs to requesting tenant.
    
    Args:
        event_id: Event identifier to fetch
        x_tenant_id: Tenant identifier header
        
    Returns:
        IngestResponse with current event status
        
    Raises:
        HTTPException: If event not found or tenant mismatch
    """
    try:
        # Validate event_id format is ULID
        try:
            ulid.parse(event_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event_id format: {event_id}"
            )
        
        # Fetch event from store (TODO: query from database)
        event_record = _ingest_events.get(event_id)
        
        if not event_record:
            logger.warning(
                "Ingest event not found",
                extra={"event_id": event_id, "tenant_id": x_tenant_id}
            )
            raise HTTPException(
                status_code=404,
                detail=f"Ingest event {event_id} not found"
            )
        
        # Verify tenant ownership
        if event_record["tenant_id"] != x_tenant_id:
            logger.warning(
                "Unauthorized ingest event access attempt",
                extra={
                    "event_id": event_id,
                    "requesting_tenant": x_tenant_id,
                    "owning_tenant": event_record["tenant_id"]
                }
            )
            raise HTTPException(
                status_code=403,
                detail="Unauthorized access to ingest event"
            )
        
        return IngestResponse(
            event_id=event_record["event_id"],
            status=event_record["status"],
            upload_id=event_record["upload_id"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to fetch ingest event",
            extra={"event_id": event_id, "error": str(e)}
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error fetching ingest event"
        )
