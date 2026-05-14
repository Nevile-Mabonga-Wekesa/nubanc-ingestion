# events.py
import json
import asyncio
import logging
from typing import Dict, Any, Coroutine

logger = logging.getLogger(__name__)


class EventPublishingError(Exception):
    """Raised when event publishing fails."""
    pass


async def publish_event(event_type: str, payload: Dict[str, Any]) -> str:
    """
    Publish event to message broker with error tracking.
    
    Args:
        event_type: Type classification of the event
        payload: Event data payload
        
    Returns:
        event_id: Unique identifier for tracking the published event
        
    Raises:
        EventPublishingError: If publication fails
    """
    event_id = None
    try:
        task: Coroutine = _fire_and_forget(event_type, payload)
        task_handle = asyncio.create_task(task)
        # Store task reference to prevent garbage collection
        task_handle.add_done_callback(_event_task_callback)
        return event_id
    except Exception as e:
        logger.error(
            "Failed to publish event",
            extra={
                "event_type": event_type,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise EventPublishingError(f"Event publication failed: {str(e)}") from e


async def _fire_and_forget(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Fire-and-forget event to broker. Replace with actual broker integration.
    
    Args:
        event_type: Type classification of the event
        payload: Event data payload
    """
    message = {
        "type": event_type,
        "payload": payload
    }
    try:
        # TODO: Replace with actual Kafka / SQS / RabbitMQ integration
        logger.info(
            "Publishing event",
            extra={
                "event_type": event_type,
                "message": json.dumps(message)
            }
        )
    except Exception as e:
        logger.error(
            "Event fire-and-forget failed",
            extra={
                "event_type": event_type,
                "error": str(e)
            }
        )


def _event_task_callback(task: asyncio.Task) -> None:
    """
    Callback to track completion of async event tasks.
    
    Args:
        task: Completed asyncio Task
    """
    try:
        if task.cancelled():
            logger.warning("Event publication task was cancelled")
        elif task.exception():
            logger.error(
                "Event publication task failed",
                extra={"error": str(task.exception())}
            )
    except asyncio.InvalidStateError:
        pass
