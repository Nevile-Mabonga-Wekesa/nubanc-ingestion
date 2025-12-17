import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Set, Literal, Optional


# ---------- Configuration ----------

RAW_MEMORY_PATH = Path("memory/raw")
FAILURE_MODE: Literal["fail_fast", "skip"] = "fail_fast"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# ---------- Domain Model ----------

@dataclass(frozen=True)
class Event:
    tenant_id: str
    version: int = 1


class EventLoadError(Exception):
    pass


# ---------- Validation ----------

def parse_event(raw: dict) -> Event:
    try:
        tenant_id = raw["tenant_id"]
    except KeyError as exc:
        raise ValueError("Event missing required field: tenant_id") from exc

    version = raw.get("version", 1)
    return Event(tenant_id=tenant_id, version=version)


# ---------- I/O Boundary ----------

def iter_events(memory_path: Path) -> Iterable[Event]:
    if not memory_path.exists() or not memory_path.is_dir():
        raise EventLoadError(f"Invalid memory path: {memory_path}")

    for year in sorted(p for p in memory_path.iterdir() if p.is_dir()):
        for month in sorted(p for p in year.iterdir() if p.is_dir()):
            for day in sorted(p for p in month.iterdir() if p.is_dir()):
                for event_file in sorted(day.glob("*.json")):
                    event = load_event(event_file)
                    if event:
                        yield event


def load_event(event_file: Path) -> Optional[Event]:
    try:
        with event_file.open(encoding="utf-8") as f:
            raw = json.load(f)
        return parse_event(raw)

    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Invalid event file: %s (%s)", event_file, exc)

        if FAILURE_MODE == "fail_fast":
            raise EventLoadError(event_file) from exc

        return None

    except OSError as exc:
        logger.error("Unreadable file: %s (%s)", event_file, exc)
        if FAILURE_MODE == "fail_fast":
            raise
        return None


# ---------- Domain Logic ----------

def replay(events: Iterable[Event]) -> dict:
    event_count = 0
    tenants: Set[str] = set()

    for event in events:
        event_count += 1
        tenants.add(event.tenant_id)

    return {
        "total_events": event_count,
        "tenants_seen": sorted(tenants),
    }


# ---------- Entry Point ----------

def main() -> None:
    events = iter_events(RAW_MEMORY_PATH)
    result = replay(events)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
