import os
from pathlib import Path
from fastapi import APIRouter

from contracts.api.infra.replay import ReplayEngine
from contracts.api.schemas.v1.replay import ReplayRequest, ReplayResponse

router = APIRouter(prefix="/v1/replay", tags=["replay"])


@router.post("", response_model=ReplayResponse)
def replay(request: ReplayRequest):
    engine = ReplayEngine(
        base_path=Path("memory"),
        env=os.getenv("NUBANC_ENV"),
    )
    return engine.replay(request)
