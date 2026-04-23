"""Global hotkey manager using pynput."""

from __future__ import annotations

import logging

from pynput import keyboard

from convoq.core.event_bus import EventBus, Events

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Listens for Ctrl+R and emits HOTKEY_TRIGGERED to show the tone picker."""

    HOTKEY = "<ctrl>+r"

    def __init__(self) -> None:
        self._listener: keyboard.GlobalHotKeys | None = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return

        self._listener = keyboard.GlobalHotKeys({
            self.HOTKEY: self._on_hotkey,
        })
        self._listener.start()
        self._running = True
        logger.info("Hotkey manager started (Ctrl+R)")

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._running = False
        logger.info("Hotkey manager stopped")

    def _on_hotkey(self) -> None:
        logger.info("Ctrl+R pressed — showing tone picker")
        EventBus.emit(Events.HOTKEY_TRIGGERED, None)

    @property
    def is_running(self) -> bool:
        return self._running
