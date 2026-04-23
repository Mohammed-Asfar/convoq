"""Tone picker popup — appears on Ctrl+R, user selects a tone to trigger refinement."""

from __future__ import annotations

import logging

from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor, QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QApplication,
)

from convoq.ai.tone import Tone
from convoq.core.event_bus import EventBus, Events

logger = logging.getLogger(__name__)

# Tone display config: tone, label, shortcut key, accent color
_TONE_CONFIG: list[tuple[Tone, str, str, str]] = [
    (Tone.CASUAL, "Casual", "1", "#6366f1"),
    (Tone.PROFESSIONAL, "Professional", "2", "#0ea5e9"),
    (Tone.FRIENDLY, "Friendly", "3", "#22c55e"),
    (Tone.DIRECT, "Direct", "4", "#f59e0b"),
    (Tone.APOLOGETIC, "Apologetic", "5", "#ef4444"),
    (Tone.TANGLISH, "Tanglish", "6", "#e879f9"),
]

_PICKER_WIDTH = 240
_BUTTON_HEIGHT = 40
_PICKER_HEIGHT = 360  # 6 buttons now


class TonePickerUI(QWidget):
    """Popup that lets the user pick a tone before refinement.

    Appears near cursor on Ctrl+R. User clicks a button or presses 1-5.
    Emits the selected tone via EventBus, then hides.
    """

    _signal_show = pyqtSignal()
    _signal_hide = pyqtSignal()

    def __init__(self) -> None:
        super().__init__(None)
        self._setup_ui()
        self._connect_signals()
        self._subscribe_events()

    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(_PICKER_WIDTH, _PICKER_HEIGHT)

        # Dark background directly on the widget
        self.setStyleSheet(
            "TonePickerUI {"
            "  background-color: #18181b;"
            "  border-radius: 12px;"
            "  border: 1px solid #333;"
            "}"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(6)

        # Title
        title = QLabel("Select Tone")
        title.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        title.setStyleSheet("color: rgba(255,255,255,0.5); padding: 0 4px 4px 4px;")
        layout.addWidget(title)

        # Tone buttons
        for tone, label, key, color in _TONE_CONFIG:
            btn = QPushButton(f"  {key}   {label}")
            btn.setFont(QFont("Segoe UI", 11))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(_BUTTON_HEIGHT)
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background-color: rgba(255,255,255,0.04);"
                f"  color: #e4e4e7;"
                f"  border: 1px solid rgba(255,255,255,0.06);"
                f"  border-left: 3px solid {color};"
                f"  border-radius: 8px;"
                f"  text-align: left;"
                f"  padding-left: 10px;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background-color: {color}30;"
                f"  border: 1px solid {color}55;"
                f"  border-left: 3px solid {color};"
                f"  color: #ffffff;"
                f"}}"
                f"QPushButton:pressed {{"
                f"  background-color: {color}50;"
                f"}}"
            )
            btn.clicked.connect(lambda checked, t=tone: self._on_tone_selected(t))
            layout.addWidget(btn)

        # Hint
        hint = QLabel("Press 1-6 or click  |  Esc to cancel")
        hint.setFont(QFont("Segoe UI", 8))
        hint.setStyleSheet("color: rgba(255,255,255,0.25); padding: 4px 0 0 0;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

    def _connect_signals(self) -> None:
        self._signal_show.connect(self._slot_show)
        self._signal_hide.connect(self._slot_hide)

    def _subscribe_events(self) -> None:
        EventBus.subscribe(Events.HOTKEY_TRIGGERED, lambda _: self._signal_show.emit())
        EventBus.subscribe(Events.REFINEMENT_STARTED, lambda _: self._signal_hide.emit())

    def _on_tone_selected(self, tone: Tone) -> None:
        logger.info("Tone selected: %s", tone.value)
        self.hide()
        EventBus.emit(Events.TONE_SELECTED, tone)

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return

        key = event.key()
        key_map = {
            Qt.Key.Key_1: Tone.CASUAL,
            Qt.Key.Key_2: Tone.PROFESSIONAL,
            Qt.Key.Key_3: Tone.FRIENDLY,
            Qt.Key.Key_4: Tone.DIRECT,
            Qt.Key.Key_5: Tone.APOLOGETIC,
            Qt.Key.Key_6: Tone.TANGLISH,
        }
        if key in key_map:
            self._on_tone_selected(key_map[key])
            return
        if key == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)

    @pyqtSlot()
    def _slot_show(self) -> None:
        import ctypes

        # Position near cursor, ensuring it stays on screen
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if screen is None:
            screen = QApplication.primaryScreen()

        screen_geo = screen.availableGeometry()

        x = cursor_pos.x() - _PICKER_WIDTH // 2
        y = cursor_pos.y() - _PICKER_HEIGHT - 20  # prefer above cursor

        # If no room above, show below
        if y < screen_geo.top():
            y = cursor_pos.y() + 20

        # Clamp to screen edges
        x = max(screen_geo.left() + 8, min(x, screen_geo.right() - _PICKER_WIDTH - 8))
        y = max(screen_geo.top() + 8, min(y, screen_geo.bottom() - _PICKER_HEIGHT - 8))

        self.move(x, y)
        self.show()
        self.raise_()

        # Force window to foreground on Windows
        # Windows blocks SetForegroundWindow from background processes,
        # but attaching to the foreground thread's input bypasses this.
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
            our_thread = user32.GetCurrentThreadId()
            if fg_thread != our_thread:
                user32.AttachThreadInput(fg_thread, our_thread, True)
                user32.SetForegroundWindow(hwnd)
                user32.AttachThreadInput(fg_thread, our_thread, False)
            else:
                user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

        self.activateWindow()
        self.setFocus()
        logger.info("Tone picker shown at (%d, %d)", x, y)

    @pyqtSlot()
    def _slot_hide(self) -> None:
        self.hide()
