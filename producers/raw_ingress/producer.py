import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


def build_raw_event(
    payload: Dict[str, Any],
    tenant_id: str,
    source_identity: str,
    *,
    schema_version: int = 1,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    event_id = str(uuid.uuid4())
    timestamp = now.isoformat()

    return {
        "event_name": "raw.payload.received.v1",
        "event_id": event_id,
        "tenant_id": tenant_id,
        "occurred_at": timestamp,
        "ingested_at": timestamp,
        "source_identity": source_identity,
        "schema_version": schema_version,
        "payload": payload,
    }


def persist_event(
    event: Dict[str, Any],
    base_path: Path,
) -> Path:
    # Fail fast if payload is not JSON serializable
    json.dumps(event)

    occurred_at = datetime.fromisoformat(event["occurred_at"])
    date_path = (
        base_path
        / f"{occurred_at.year:04d}"
        / f"{occurred_at.month:02d}"
        / f"{occurred_at.day:02d}"
    )

    date_path.mkdir(parents=True, exist_ok=True)

    file_path = date_path / f"{event['event_id']}.json"

    tmp_path = file_path.with_suffix(".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(event, f, indent=2)

    # Atomic rename
    tmp_path.replace(file_path)

    return file_path


def emit_raw_payload(
    payload: Dict[str, Any],
    tenant_id: str,
    source_identity: str,
    *,
    base_path: Path = Path("memory/raw"),
) -> Path:
    event = build_raw_event(
        payload=payload,
        tenant_id=tenant_id,
        source_identity=source_identity,
    )
    return persist_event(event, base_path)


if __name__ == "__main__":
    path = emit_raw_payload(
        payload={"example": "hello continuum"},
        tenant_id="tenant_demo",
        source_identity="local-test",
    )
    print(f"Event written to {path}")
