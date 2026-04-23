"""Facade — single entry point that hides the entire Convoq subsystem."""

from __future__ import annotations

import logging
import sys

from PyQt6.QtWidgets import QApplication

from convoq.adapters.whatsapp import WhatsAppAdapter  # noqa: F401 — triggers self-registration
from convoq.config.config_manager import ConfigManager
from convoq.core.event_bus import EventBus
from convoq.core.pipeline import RefinementPipeline
from convoq.hotkeys.manager import HotkeyManager
from convoq.ui.overlay import OverlayUI
from convoq.ui.tone_picker import TonePickerUI
from convoq.ui.tray import TrayManager

logger = logging.getLogger(__name__)


class ConvoqEngine:
    """Facade — the only class main.py needs to interact with.

    Initializes and coordinates all subsystems:
    - ConfigManager (singleton, auto-loaded)
    - HotkeyManager (global hotkey listener)
    - RefinementPipeline (orchestrator)
    - OverlayUI (PyQt6 overlay)
    - TrayManager (system tray)
    """

    def __init__(self) -> None:
        self._config = ConfigManager()
        self._app: QApplication | None = None
        self._pipeline: RefinementPipeline | None = None
        self._hotkeys: HotkeyManager | None = None
        self._tone_picker: TonePickerUI | None = None
        self._overlay: OverlayUI | None = None
        self._tray: TrayManager | None = None

    def start(self) -> None:
        logger.info("Starting Convoq engine...")

        # PyQt6 app must be created first (UI thread)
        self._app = QApplication.instance() or QApplication(sys.argv)

        # Initialize components
        self._pipeline = RefinementPipeline()
        self._hotkeys = HotkeyManager()
        self._tone_picker = TonePickerUI()
        self._overlay = OverlayUI()
        self._tray = TrayManager(
            on_toggle=self._on_toggle,
            on_exit=self._on_exit,
        )

        # Start subsystems
        self._pipeline.start()
        self._hotkeys.start()
        self._tray.start()

        logger.info("Convoq engine started — listening for hotkeys")

        # Run Qt event loop (blocks until exit)
        self._app.exec()

    def stop(self) -> None:
        logger.info("Stopping Convoq engine...")
        if self._hotkeys:
            self._hotkeys.stop()
        if self._pipeline:
            self._pipeline.stop()
        if self._tray:
            self._tray.stop()
        if self._app:
            self._app.quit()
        EventBus.clear()
        logger.info("Convoq engine stopped")

    def _on_toggle(self, enabled: bool) -> None:
        if enabled:
            if self._pipeline:
                self._pipeline.start()
            if self._hotkeys:
                self._hotkeys.start()
            logger.info("Convoq enabled")
        else:
            if self._hotkeys:
                self._hotkeys.stop()
            if self._pipeline:
                self._pipeline.stop()
            logger.info("Convoq disabled")

    def _on_exit(self) -> None:
        self.stop()
