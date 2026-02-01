import os
from pathlib import Path
from fastapi import APIRouter

from contracts.api.infra.health_consistency import HealthConsistencyChecker
from contracts.api.schemas.v1.health import HealthConsistencyResponse

router = APIRouter(prefix="/v1/health", tags=["health"])


@router.get("/consistency", response_model=HealthConsistencyResponse)
def health_consistency():
    checker = HealthConsistencyChecker(
        base_path=Path("memory"),
        env=os.getenv("NUBANC_ENV"),
    )
    return checker.check()
