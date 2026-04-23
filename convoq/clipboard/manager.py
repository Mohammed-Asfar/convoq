"""Proxy pattern — safe clipboard access with locking and backup/restore."""

from __future__ import annotations

import logging
import threading
import time

import pyperclip

from convoq.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ClipboardManager:
    """Proxy around the system clipboard.

    Adds thread-safe locking, backup/restore of prior clipboard
    contents, and configurable delays to avoid race conditions.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._backup: str | None = None
        config = ConfigManager()
        self._paste_delay = config.get("clipboard.paste_delay_ms", 50) / 1000
        self._restore_delay = config.get("clipboard.restore_delay_ms", 100) / 1000

    def read(self) -> str:
        with self._lock:
            try:
                return pyperclip.paste() or ""
            except Exception:
                logger.exception("Failed to read clipboard")
                return ""

    def write(self, text: str) -> None:
        with self._lock:
            try:
                pyperclip.copy(text)
            except Exception:
                logger.exception("Failed to write to clipboard")

    def backup(self) -> None:
        self._backup = self.read()

    def restore(self) -> None:
        if self._backup is not None:
            time.sleep(self._restore_delay)
            self.write(self._backup)
            self._backup = None

    def safe_inject(self, text: str) -> None:
        """Backup clipboard, inject text via paste, then restore original contents."""
        import pyautogui

        self.backup()
        self.write(text)
        time.sleep(self._paste_delay)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(self._paste_delay)
        self.restore()

    def safe_select_all_and_read(self) -> str:
        """Select all text in the active input field and read it."""
        import pyautogui

        self.backup()
        pyautogui.hotkey("ctrl", "a")
        time.sleep(self._paste_delay)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(self._paste_delay)
        text = self.read()
        self.restore()
        return text
