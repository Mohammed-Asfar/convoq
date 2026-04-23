"""Groq-powered refiner with streaming support."""

from __future__ import annotations

import logging
from typing import AsyncIterator

from groq import Groq

from convoq.ai.base import Refiner
from convoq.ai.prompt_builder import PromptBuilder
from convoq.ai.tone import Tone
from convoq.config.config_manager import ConfigManager
from convoq.models.context import ConversationContext

logger = logging.getLogger(__name__)


class GroqRefiner(Refiner):
    """Concrete refiner using Groq's streaming API.

    Sends a structured prompt and yields tokens as they stream back.
    """

    def __init__(self) -> None:
        config = ConfigManager()
        api_key = config.get("ai.api_key", "")
        if not api_key:
            raise ValueError(
                "Groq API key not configured. "
                "Set GROQ_API_KEY env var or add it to ~/.convoq/config.yaml"
            )
        self._client = Groq(api_key=api_key)
        self._model = config.get("ai.model", "llama-3.1-8b-instant")
        self._max_tokens = config.get("ai.max_tokens", 256)
        self._temperature = config.get("ai.temperature", 0.7)

    async def refine(
        self,
        draft: str,
        context: ConversationContext,
        tone: Tone,
    ) -> AsyncIterator[str]:
        system_prompt, user_prompt = (
            PromptBuilder()
            .with_system_instructions()
            .with_context(context)
            .with_draft(draft)
            .with_tone(tone)
            .with_constraints()
            .build()
        )

        logger.debug("Sending refinement request (model=%s, tone=%s)", self._model, tone.value)

        # Groq SDK uses sync streaming — we wrap it for our async interface
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def refine_sync(
        self,
        draft: str,
        context: ConversationContext,
        tone: Tone,
    ) -> str:
        """Synchronous refinement — collects full response. Used by pipeline."""
        system_prompt, user_prompt = (
            PromptBuilder()
            .with_system_instructions()
            .with_context(context)
            .with_draft(draft)
            .with_tone(tone)
            .with_constraints()
            .build()
        )

        stream = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self._max_tokens,
            temperature=self._temperature,
            stream=True,
        )

        tokens: list[str] = []
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                tokens.append(delta.content)
        return "".join(tokens)
