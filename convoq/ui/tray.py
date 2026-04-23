"""System tray manager — background lifecycle control."""

from __future__ import annotations

import logging
import threading
from typing import Callable

from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

logger = logging.getLogger(__name__)


class TrayManager:
    """System tray icon with enable/disable toggle and exit.

    Runs pystray in its own thread to avoid blocking the main event loop.
    """

    def __init__(
        self,
        on_toggle: Callable[[bool], None] | None = None,
        on_exit: Callable[[], None] | None = None,
    ) -> None:
        self._on_toggle = on_toggle
        self._on_exit = on_exit
        self._enabled = True
        self._icon: Icon | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._icon = Icon(
            "Convoq",
            icon=self._create_icon(),
            title="Convoq — Active",
            menu=self._build_menu(),
        )
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()
        logger.info("System tray started")

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
            self._icon = None
        logger.info("System tray stopped")

    def _build_menu(self) -> Menu:
        return Menu(
            MenuItem(
                "Enabled",
                self._toggle,
                checked=lambda _: self._enabled,
            ),
            Menu.SEPARATOR,
            MenuItem("Exit", self._exit),
        )

    def _toggle(self, icon: Icon, item: MenuItem) -> None:
        self._enabled = not self._enabled
        status = "Active" if self._enabled else "Paused"
        icon.title = f"Convoq — {status}"
        logger.info("Convoq %s", status.lower())
        if self._on_toggle:
            self._on_toggle(self._enabled)

    def _exit(self, icon: Icon, item: MenuItem) -> None:
        logger.info("Exit requested from tray")
        if self._on_exit:
            self._on_exit()
        icon.stop()

    @staticmethod
    def _create_icon() -> Image.Image:
        """Generate a simple tray icon (blue circle with 'C')."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, size - 4, size - 4], fill=(59, 130, 246))
        draw.text((20, 14), "C", fill="white")
        return img

    @property
    def is_enabled(self) -> bool:
        return self._enabled
