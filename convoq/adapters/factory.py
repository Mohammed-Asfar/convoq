"""Factory Method pattern — creates the correct AppAdapter for the active window."""

from __future__ import annotations

import logging

from convoq.adapters.base import AppAdapter
from convoq.adapters.detection import get_foreground_window_title

logger = logging.getLogger(__name__)


class UnsupportedAppError(Exception):
    """Raised when no adapter is registered for the active app."""


class AppAdapterFactory:
    """Factory that creates AppAdapters based on the active foreground window.

    New adapters register themselves via `register()` — no modification
    to existing code needed (OCP).
    """

    _registry: dict[str, type[AppAdapter]] = {}

    @classmethod
    def register(cls, app_keyword: str, adapter_cls: type[AppAdapter]) -> None:
        cls._registry[app_keyword.lower()] = adapter_cls
        logger.info("Registered adapter: %s → %s", app_keyword, adapter_cls.__name__)

    @classmethod
    def create_for_active_window(cls) -> AppAdapter:
        title = get_foreground_window_title()
        for keyword, adapter_cls in cls._registry.items():
            if keyword in title.lower():
                return adapter_cls()
        raise UnsupportedAppError(
            f"No adapter registered for window: '{title}'"
        )

    @classmethod
    def get_supported_apps(cls) -> list[str]:
        return list(cls._registry.keys())
