"""Abstract base for context extractors — Chain of Responsibility nodes."""

from __future__ import annotations

from abc import ABC, abstractmethod

from convoq.models.context import ConversationContext


class ExtractionError(Exception):
    """Raised when a specific extraction method fails."""


class ContextExtractor(ABC):
    """Abstract context extractor.

    Each concrete extractor implements one extraction strategy
    (UI automation, accessibility API, OCR, etc.).
    """

    @abstractmethod
    def extract(self, window_handle: int | None = None) -> ConversationContext:
        """Extract conversation context from the target application.

        Args:
            window_handle: Optional OS window handle to target.

        Returns:
            ConversationContext with extracted messages.

        Raises:
            ExtractionError: If this extractor cannot handle the current state.
        """

    @abstractmethod
    def can_handle(self, app_name: str) -> bool:
        """Return True if this extractor supports the given app."""
