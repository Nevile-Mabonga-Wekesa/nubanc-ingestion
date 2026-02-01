import os
from pathlib import Path
from fastapi import APIRouter, HTTPException

from contracts.api.infra.ingest_status import IngestStatusReader
from contracts.api.schemas.v1.ingest.status import IngestStatusResponse

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])


@router.get("/{event_id}", response_model=IngestStatusResponse)
def get_ingest_status(event_id: str):
    env = os.getenv("NUBANC_ENV")
    reader = IngestStatusReader(
        base_path=Path("memory"),
        env=env,
    )

    try:
        return reader.read(event_id=event_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="event not found")
