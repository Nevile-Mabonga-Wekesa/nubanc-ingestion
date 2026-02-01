from datetime import datetime, timezone
from typing import Optional
from .models import StateResponse, Confidence, DerivedFrom


def compute_entity_state(
    *,
    env: str,
    tenant_id: str,
    entity_type: str,
    entity_id: str,
    as_of: Optional[str],
) -> StateResponse:
    """
    Single authority for system truth.
    Deterministic. Side_effect free.
    """

    # ---- Placeholder system reads (replace with real projections) ----
    raw_events = 142
    normalized_events = 138
    failed_events = raw_events - normalized_events

    inconsistencies = []
    confidence_level = "high"

    if failed_events > 0:
        inconsistencies.append("missing_normalized_events")
        confidence_level = "degraded"

    # ---- Example derived state (ledger projection) ----
    state = {
        "balance": 1250.75,
        "currency": "USD",
        "status": "active",
    }

    return StateResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        state=state,
        state_version="ledger:v3",
        derived_from=DerivedFrom(
            raw_events=raw_events,
            normalized_events=normalized_events,
            failed_events=failed_events,
        ),
        last_updated_at=datetime.now(timezone.utc),
        confidence=Confidence(
            level=confidence_level,
            reasons=inconsistencies,
        ),
        inconsistencies=inconsistencies,
        replay_safe=True,
    )
