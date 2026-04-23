"""WhatsApp Desktop adapter — concrete AppAdapter implementation."""

from __future__ import annotations

import ctypes
import logging
import time

import pyautogui
import pyperclip

from convoq.adapters.base import AppAdapter
from convoq.adapters.detection import get_foreground_window_title, get_foreground_window_handle
from convoq.adapters.factory import AppAdapterFactory
from convoq.models.context import ConversationContext

logger = logging.getLogger(__name__)


class WhatsAppAdapter(AppAdapter):
    """Adapter for WhatsApp Desktop on Windows.

    Handles draft reading via clipboard and text replacement
    via clipboard injection. Context extraction returns empty
    for now (UI automation is fragile across WhatsApp versions).
    """

    def __init__(self) -> None:
        self._whatsapp_hwnd: int = 0

    @property
    def app_name(self) -> str:
        return "whatsapp"

    def is_active(self) -> bool:
        title = get_foreground_window_title()
        return "whatsapp" in title.lower()

    def extract_context(self) -> ConversationContext:
        # Return empty context for MVP — context extraction via UI automation
        # is fragile and breaks across WhatsApp versions.
        # The AI still refines grammar/tone without context.
        return ConversationContext.empty()

    def get_draft(self) -> str:
        """Read the draft from WhatsApp's input field.

        Saves the WhatsApp window handle so we can refocus it
        before replacing text (in case overlay stole focus).
        """
        self._whatsapp_hwnd = get_foreground_window_handle()

        # Save current clipboard
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = ""

        # Select all in input field and copy
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.1)

        # Read the draft
        try:
            draft = pyperclip.paste()
        except Exception:
            draft = ""

        # Restore old clipboard
        try:
            if old_clipboard and old_clipboard != draft:
                pyperclip.copy(old_clipboard)
        except Exception:
            pass

        logger.info("Draft captured (%d chars): '%s'", len(draft), draft[:50])
        return draft

    def replace_text(self, text: str) -> None:
        """Replace the input field text with the refined message."""
        # Refocus WhatsApp window (overlay or other windows may have stolen focus)
        if self._whatsapp_hwnd:
            try:
                ctypes.windll.user32.SetForegroundWindow(self._whatsapp_hwnd)
                time.sleep(0.2)
            except Exception:
                logger.warning("Failed to refocus WhatsApp window")

        # Select all text in the input field again, then paste over it
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)

        # Copy refined text to clipboard and paste
        pyperclip.copy(text)
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.1)

        logger.info("Text replaced (%d chars): '%s'", len(text), text[:50])


# Self-registration — OCP: adding a new app only requires a new file
AppAdapterFactory.register("whatsapp", WhatsAppAdapter)
