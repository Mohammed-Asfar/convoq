"""Abstract AppAdapter — Adapter pattern + ISP protocols."""

from __future__ import annotations

from abc import ABC, abstractmethod

from convoq.models.context import ConversationContext


class AppAdapter(ABC):
    """Abstract adapter for messaging applications.

    Each concrete adapter (WhatsApp, Slack, Teams) implements
    context extraction, draft reading, and text replacement
    specific to that app's UI.
    """

    @property
    @abstractmethod
    def app_name(self) -> str:
        """Unique identifier for this app."""

    @abstractmethod
    def is_active(self) -> bool:
        """Return True if this app's window is currently in the foreground."""

    @abstractmethod
    def extract_context(self) -> ConversationContext:
        """Extract recent conversation context from the app."""

    @abstractmethod
    def get_draft(self) -> str:
        """Read the current draft text from the app's input field."""

    @abstractmethod
    def replace_text(self, text: str) -> None:
        """Replace the current draft with the refined text."""
