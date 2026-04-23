"""Observer pattern — decoupled event system for inter-component communication."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventBus:
    """Central event bus using the Observer pattern.

    Components publish and subscribe to named events without
    knowing about each other.
    """

    _listeners: dict[str, list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event: str, callback: Callable) -> None:
        cls._listeners[event].append(callback)

    @classmethod
    def unsubscribe(cls, event: str, callback: Callable) -> None:
        try:
            cls._listeners[event].remove(callback)
        except ValueError:
            pass

    @classmethod
    def emit(cls, event: str, data: Any = None) -> None:
        for callback in cls._listeners.get(event, []):
            try:
                callback(data)
            except Exception:
                logger.exception("Error in event handler for '%s'", event)

    @classmethod
    def clear(cls) -> None:
        cls._listeners.clear()


# Event name constants
class Events:
    HOTKEY_TRIGGERED = "hotkey.triggered"
    TONE_SELECTED = "tone.selected"
    REFINEMENT_STARTED = "refinement.started"
    REFINEMENT_TOKEN = "refinement.token"
    REFINEMENT_COMPLETED = "refinement.completed"
    REFINEMENT_FAILED = "refinement.failed"
    APP_DETECTED = "app.detected"
