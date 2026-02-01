# Contracts/api/v1/uploads/normalize.py
from fastapi import APIRouter, Header, HTTPException
from pathlib import Path
from typing import List
import os

from contracts.api.schemas.v1.uploads.normalize import NormalizeRequest, NormalizeResponse
from contracts.events.envelope import NormalizedEvent
from infra.memory_store import write_event, read_event
from infra.failure_writer import write_failure

router = APIRouter(prefix="/v1/uploads", tags=["uploads"])

@router.post("/{upload_id}/normalize", response_model=NormalizeResponse, status_code=202)
async def normalize_upload(
    upload_id: str,
    body: NormalizeRequest,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id")
):
    env = os.getenv("NUBANC_ENV", "dev")
    normalized_event_ids: List[str] = []

    for event_id in body.event_ids:
        try:
            raw_event = read_event(env, "raw", event_id)
        except FileNotFoundError:

            write_failure(
                env=env,
                event_id=event_id,
                stage="normalization",
                code="NOT_FOUND",
                reason="Raw event missing",
            )

            continue

        try:
            # Veteran principle: No domain assumptions, pure translation
            nevt = NormalizedEvent(
                event_id="",  # will be set in memory store
                tenant_id=x_tenant_id,
                upload_id=upload_id,
                normalization_version=body.normalization_version,
                payload=raw_event.get("records", {})  # simple structural normalization
            )
            nevt_id = write_event(env, nevt.dict(), folder="normalized")
            normalized_event_ids.append(nevt_id)
        except Exception as e:
            write_failure(env, event_id, stage="normalization", code="TRANSLATION_ERROR", reason=str(e))
            continue

    if not normalized_event_ids:
        raise HTTPException(status_code=400, detail="No events could be normalized")

    return NormalizeResponse(
        status="accepted",
        upload_id=upload_id,
        events_normalized=len(normalized_event_ids),
        normalized_event_ids=normalized_event_ids
    )
