import json
import hashlib
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Protocol

from replay.replay_engine import load_events

# -----------------------------
# Configuration
# -----------------------------

# Environment variable or default path
EVENT_FILE = os.getenv("EVENT_FILE", "memory/events.json")

LEDGER_PATH = Path(os.getenv("LEDGER_PATH", "memory/ledger"))
DECISION_NAMESPACE = "decision.credit_stage"
DECISION_VERSION = "v1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Domain Contracts
# -----------------------------

@dataclass(frozen=True)
class Event:
    tenant_id: str

    @staticmethod
    def from_raw(raw: Dict) -> "Event":
        try:
            return Event(tenant_id=str(raw["tenant_id"]))
        except KeyError:
            raise ValueError("Invalid event: tenant_id missing")

    def fingerprint(self) -> str:
        return hashlib.sha256(self.tenant_id.encode()).hexdigest()


@dataclass(frozen=True)
class Decision:
    tenant_id: str
    stage: str
    event_count: int
    input_fingerprint: str

    @property
    def name(self) -> str:
        return f"{DECISION_NAMESPACE}.{DECISION_VERSION}"

    def deterministic_id(self) -> str:
        source = (
            f"{self.tenant_id}|"
            f"{self.name}|"
            f"{self.stage}|"
            f"{self.event_count}|"
            f"{self.input_fingerprint}"
        )
        return hashlib.sha256(source.encode()).hexdigest()

    def to_record(self) -> Dict:
        return {
            "decision_id": self.deterministic_id(),
            "decision_name": self.name,
            "tenant_id": self.tenant_id,
            "result": self.stage,
            "inputs": {
                "event_count": self.event_count,
                "input_fingerprint": self.input_fingerprint,
            },
        }

# -----------------------------
# Rule Abstraction
# -----------------------------

class DecisionRule(Protocol):
    def evaluate(self, events: Iterable[Event]) -> List[Decision]:
        ...


def evaluate(events: Iterable[Event]) -> List[Decision]:
    tenant_events: Dict[str, List[Event]] = {}

    for event in events:
        tenant_events.setdefault(event.tenant_id, []).append(event)

    decisions: List[Decision] = []

    for tenant_id, evts in tenant_events.items():
        stage = "stage_1" if len(evts) >= 1 else "unknown"

        fingerprint_source = "".join(e.fingerprint() for e in evts)
        input_fp = hashlib.sha256(fingerprint_source.encode()).hexdigest()

        decisions.append(
            Decision(
                tenant_id=tenant_id,
                stage=stage,
                event_count=len(evts),
                input_fingerprint=input_fp,
            )
        )

    return decisions


class CreditStageRule:
    pass

# -----------------------------
# Persistence Abstraction
# -----------------------------

class DecisionStore(Protocol):
    def save(self, record: Dict) -> None:
        ...


class FileLedgerStore:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, record: Dict) -> None:
        decision_id = record["decision_id"]
        final_path = self.base_path / f"{decision_id}.json"
        temp_path = final_path.with_suffix(".tmp")

        if final_path.exists():
            logger.debug("Decision already exists: %s", decision_id)
            return

        with open(temp_path, "w") as f:
            json.dump(record, f, indent=2)

        temp_path.replace(final_path)
        logger.info("Decision recorded: %s", decision_id)

# -----------------------------
# Orchestration
# -----------------------------

class DecisionEngine:
    def __init__(self, rules: List[DecisionRule], store: DecisionStore):
        self.rules = rules
        self.store = store

    def run(self, raw_events: Iterable[Dict]) -> None:
        events: List[Event] = []

        for raw in raw_events:
            try:
                events.append(Event.from_raw(raw))
            except ValueError as e:
                logger.warning("Skipping event: %s", e)

        for rule in self.rules:
            decisions = rule.evaluate(events)
            for decision in decisions:
                self.store.save(decision.to_record())

# -----------------------------
# Entry Point
# -----------------------------

def main():
    event_path = Path(EVENT_FILE)
    if not event_path.exists():
        logger.warning(f"Event file not found: {event_path}. Creating empty file.")
        event_path.parent.mkdir(parents=True, exist_ok=True)
        event_path.write_text("[]")  # empty JSON array

    # Pass a string path to load_events
    raw_events = load_events(event_path)

    engine = DecisionEngine(
        rules=[CreditStageRule()],
        store=FileLedgerStore(LEDGER_PATH),
    )
    engine.run(raw_events)

if __name__ == "__main__":
    main()
