"""Data models for conversation context and refinement."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from convoq.ai.tone import Tone


@dataclass(frozen=True)
class Message:
    """A single message in a conversation."""

    text: str
    sender: str  # "self" or contact name
    timestamp: str | None = None

    def __str__(self) -> str:
        return f"[{self.sender}]: {self.text}"


@dataclass(frozen=True)
class ConversationContext:
    """Extracted conversation context from a messaging app."""

    messages: tuple[Message, ...] = ()
    app_name: str = "unknown"
    is_group: bool = False

    def is_valid(self) -> bool:
        return len(self.messages) > 0

    @classmethod
    def empty(cls) -> ConversationContext:
        return cls(messages=(), app_name="unknown")

    def format_for_prompt(self) -> str:
        if not self.messages:
            return "(No prior messages available)"
        return "\n".join(str(msg) for msg in self.messages)


@dataclass(frozen=True)
class RefinementRequest:
    """Input to the refinement pipeline."""

    draft: str
    context: ConversationContext
    tone: Tone


@dataclass
class RefinementResult:
    """Output from the refinement pipeline."""

    original: str
    refined: str
    tone: Tone
    latency_ms: float = 0.0
