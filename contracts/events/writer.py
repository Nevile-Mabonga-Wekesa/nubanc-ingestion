# events/writer.py
from pathlib import Path
import json
from datetime import datetime
import uuid

def write_raw_event(env: str, event_type: str, payload: dict, identity: dict, tenant_id: str):
    event_id = str(uuid.uuid4())
    path = Path(f"memory/{env}/raw/{datetime.utcnow().date()}")
    path.mkdir(parents=True, exist_ok=True)

    event = {
        "event_id": event_id,
        "event_type": event_type,
        "occurred_at": datetime.utcnow().isoformat(),
        "environment": env,
        "tenant_id": tenant_id,
        "identity": identity,
        "payload": payload
    }

    file_path = path / f"{event_id}.json"
    file_path.write_text(json.dumps(event, indent=2))

    return str(file_path)
