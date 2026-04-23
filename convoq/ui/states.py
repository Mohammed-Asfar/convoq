"""State pattern — overlay UI states."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from convoq.ui.overlay import OverlayUI


class OverlayState(ABC):
    """Abstract state for the overlay UI."""

    @abstractmethod
    def enter(self, overlay: OverlayUI) -> None:
        """Called when transitioning into this state."""

    @abstractmethod
    def exit(self, overlay: OverlayUI) -> None:
        """Called when transitioning out of this state."""


class HiddenState(OverlayState):
    def enter(self, overlay: OverlayUI) -> None:
        overlay.hide()

    def exit(self, overlay: OverlayUI) -> None:
        pass


class LoadingState(OverlayState):
    def enter(self, overlay: OverlayUI) -> None:
        overlay.set_text("Refining...")
        overlay.show_at_cursor()

    def exit(self, overlay: OverlayUI) -> None:
        pass


class StreamingState(OverlayState):
    def enter(self, overlay: OverlayUI) -> None:
        # Text is updated token-by-token via overlay.append_token()
        pass

    def exit(self, overlay: OverlayUI) -> None:
        pass


class ErrorState(OverlayState):
    def __init__(self, message: str = "Error") -> None:
        self._message = message

    def enter(self, overlay: OverlayUI) -> None:
        overlay.set_text(f"⚠ {self._message}")
        overlay.start_fade_timer()

    def exit(self, overlay: OverlayUI) -> None:
        pass


class FadingState(OverlayState):
    def enter(self, overlay: OverlayUI) -> None:
        overlay.start_fade_timer()

    def exit(self, overlay: OverlayUI) -> None:
        overlay.stop_fade_timer()
