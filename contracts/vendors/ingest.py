import os
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, Request

from contracts.api.schemas.v1.vendors.ingest import VendorIngestResponse
from contracts.vendors.registry import get_translator
from contracts.events.writer import write_raw_event
from infra.failure_writer import write_failure

router = APIRouter(prefix="/v1/vendors", tags=["vendors"])


@router.post("")
async def vendor_ingest():
    env = os.getenv("NUBANC_ENV")
    if not env:
        raise HTTPException(500, "NUBANC_ENV not set")

    payload = await request.json()

    try:
        translator = get_translator(vendor)
        events = translator.translate(
            tenant_id=x_tenant_id,
            vendor_version=x_vendor_version,
            payload=payload,
        )
    except KeyError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        # Translation failure is a fact
        failure_event_id = "evt_translation_failed"
        write_failure(
            base_path=Path("memory"),
            env=env,
            event_id=failure_event_id,
            code="TRANSLATION_ERROR",
            stage="ingestion",
            reason=str(e),
        )
        raise HTTPException(400, "Vendor payload translation failed")

    event_ids = []
    for ce in events:
        event_ids.append(
            write_raw_event(
                base_path=Path("memory"),
                env=env,
                event=ce.dict(),
            )
        )

    return VendorIngestResponse(
        status="accepted",
        vendor=vendor,
        events_emitted=len(event_ids),
        event_ids=event_ids,
    )
