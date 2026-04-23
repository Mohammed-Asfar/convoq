"""Active window detection — identifies which messaging app is in the foreground."""

from __future__ import annotations

import ctypes
import logging

logger = logging.getLogger(__name__)


def get_foreground_window_title() -> str:
    """Get the title of the currently focused window (Windows only)."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        logger.exception("Failed to get foreground window title")
        return ""


def get_foreground_window_handle() -> int:
    """Get the handle of the currently focused window."""
    try:
        return ctypes.windll.user32.GetForegroundWindow()
    except Exception:
        return 0
