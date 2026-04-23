"""Overlay UI — lightweight PyQt6 popup with State pattern."""

from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout

from convoq.config.config_manager import ConfigManager
from convoq.core.event_bus import EventBus, Events
from convoq.ui.states import (
    ErrorState,
    FadingState,
    HiddenState,
    LoadingState,
    OverlayState,
    StreamingState,
)

logger = logging.getLogger(__name__)


class OverlayUI(QWidget):
    """Frameless overlay widget that shows refinement status.

    Uses the State pattern to manage transitions:
    Hidden → Loading → Streaming → Fading → Hidden
                ↓           ↓
              Error       Error

    All state transitions are routed through Qt signals so they
    execute on the main thread — even when triggered from background threads.
    """

    # Thread-safe signals — these marshal calls to the Qt main thread
    _signal_show_loading = pyqtSignal()
    _signal_show_fading = pyqtSignal()
    _signal_show_error = pyqtSignal(str)
    _signal_append_token = pyqtSignal(str)
    _signal_set_text = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        config = ConfigManager()
        self._fade_timeout = config.get("overlay.fade_timeout_ms", 1500)
        self._state: OverlayState = HiddenState()

        self._setup_ui()
        self._connect_signals()
        self._subscribe_events()

    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedWidth(280)
        self.setStyleSheet(
            "OverlayUI {"
            "  background-color: #1e1e1e;"
            "  border-radius: 8px;"
            "  border: 1px solid #333;"
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        self._label = QLabel("Refining...")
        self._label.setFont(QFont("Segoe UI", 11))
        self._label.setStyleSheet("color: #ffffff; padding: 10px 14px;")
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

        # Fade timer
        self._fade_timer = QTimer(self)
        self._fade_timer.setSingleShot(True)
        self._fade_timer.timeout.connect(self._on_fade_timeout)

    def _connect_signals(self) -> None:
        """Connect signals to slots — ensures all UI work runs on the main thread."""
        self._signal_show_loading.connect(self._slot_show_loading)
        self._signal_show_fading.connect(self._slot_show_fading)
        self._signal_show_error.connect(self._slot_show_error)
        self._signal_append_token.connect(self._slot_append_token)
        self._signal_set_text.connect(self._slot_set_text)

    def _subscribe_events(self) -> None:
        """Subscribe to EventBus — callbacks emit signals (thread-safe)."""
        EventBus.subscribe(Events.REFINEMENT_STARTED, lambda _: self._signal_show_loading.emit())
        EventBus.subscribe(Events.REFINEMENT_TOKEN, lambda token: self._signal_append_token.emit(token))
        EventBus.subscribe(Events.REFINEMENT_COMPLETED, lambda _: self._signal_show_fading.emit())
        EventBus.subscribe(Events.REFINEMENT_FAILED, lambda msg: self._signal_show_error.emit(str(msg)))

    # ── Slots (always run on Qt main thread) ─────────────────────

    @pyqtSlot()
    def _slot_show_loading(self) -> None:
        self._transition_to(LoadingState())

    @pyqtSlot()
    def _slot_show_fading(self) -> None:
        self._transition_to(FadingState())

    @pyqtSlot(str)
    def _slot_show_error(self, message: str) -> None:
        self._transition_to(ErrorState(message))

    @pyqtSlot(str)
    def _slot_append_token(self, token: str) -> None:
        if isinstance(self._state, LoadingState):
            self._transition_to(StreamingState())
            self._label.setText(token)
        else:
            self._label.setText(self._label.text() + token)
        self.adjustSize()

    @pyqtSlot(str)
    def _slot_set_text(self, text: str) -> None:
        self._label.setText(text)
        self.adjustSize()

    # ── State transitions (main thread only) ─────────────────────

    def _transition_to(self, new_state: OverlayState) -> None:
        self._state.exit(self)
        self._state = new_state
        self._state.enter(self)

    def set_text(self, text: str) -> None:
        self._signal_set_text.emit(text)

    def show_at_cursor(self) -> None:
        pos = QCursor.pos()
        self.move(pos.x() + 15, pos.y() + 15)
        self.show()
        self.raise_()

    def start_fade_timer(self) -> None:
        self._fade_timer.start(self._fade_timeout)

    def stop_fade_timer(self) -> None:
        self._fade_timer.stop()

    def _on_fade_timeout(self) -> None:
        self.hide()
        self._transition_to(HiddenState())
