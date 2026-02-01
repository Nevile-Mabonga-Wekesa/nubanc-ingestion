import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response

from contracts.api.infra.failure_reader import FailureReader
from contracts.api.schemas.v1.ingest.failure import IngestFailureResponse

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])


@router.get("/{event_id}/failure", response_model=IngestFailureResponse)
def get_ingest_failure(event_id: str):
    reader = FailureReader(
        base_path=Path("memory"),
        env=os.getenv("NUBANC_ENV"),
    )

    try:
        return reader.read(event_id)
    except FileNotFoundError:
        # event exists but has never failed OR never existed
        return Response(status_code=204)
