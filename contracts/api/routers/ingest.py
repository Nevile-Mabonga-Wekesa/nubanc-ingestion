# contracts/api/routes/ingest.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/v1/ingest", tags=["Ingest"])


class IngestRequest(BaseModel):
    upload_id: str
    source_type: str
    format: str


class IngestResponse(BaseModel):
    event_id: str
    status: str


@router.post("/", response_model=IngestResponse, status_code=201)
def create_ingest_event(payload: IngestRequest):
    """
    Create an ingestion event and return an event_id.
    """
    event_id = str(uuid.uuid4())
    return {"event_id": event_id, "status": "PENDING"}


@router.get("/{event_id}", response_model=IngestResponse)
def get_ingest_event(event_id: str):
    """
    Fetch ingestion status by event_id.
    """
    try:
        uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event_id")

    return {"event_id": event_id, "status": "PENDING"}