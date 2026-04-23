"""Abstract Refiner — DIP ensures pipeline depends on this, not concrete AI clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from convoq.ai.tone import Tone
from convoq.models.context import ConversationContext


class Refiner(ABC):
    """Abstract AI refiner.

    Concrete implementations (Groq, OpenAI, local model) must
    implement the streaming refine method.
    """

    @abstractmethod
    async def refine(
        self,
        draft: str,
        context: ConversationContext,
        tone: Tone,
    ) -> AsyncIterator[str]:
        """Refine a draft message using AI, yielding tokens as they arrive.

        Args:
            draft: The user's raw draft message.
            context: Extracted conversation context.
            tone: The desired tone for the refined message.

        Yields:
            Individual tokens/chunks of the refined message.
        """
        ...  # pragma: no cover
