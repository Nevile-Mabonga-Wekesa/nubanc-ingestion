import json
from pathlib import Path

from contracts.api.schemas.v1.ingest.failure import IngestFailureResponse


class FailureReader:
    def __init__(self, *, base_path: Path, env: str):
        if not env:
            raise RuntimeError("NUBANC_ENV must be set")

        self.root = base_path / env / "failures"

    def read(self, event_id: str) -> IngestFailureResponse:
        path = self.root / f"{event_id}.json"

        if not path.exists():
            raise FileNotFoundError(event_id)

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return IngestFailureResponse(**data)
