"""Builder pattern — constructs refinement prompts step by step."""

from __future__ import annotations

from convoq.ai.tone import Tone
from convoq.models.context import ConversationContext


class PromptBuilder:
    """Builds structured prompts for the AI refiner.

    Usage:
        prompt = (
            PromptBuilder()
            .with_system_instructions()
            .with_context(context)
            .with_draft(draft)
            .with_tone(tone)
            .build()
        )
    """

    def __init__(self) -> None:
        self._system: str = ""
        self._user_parts: list[str] = []

    def with_system_instructions(self) -> PromptBuilder:
        self._system = (
            "You are an AI message assistant that refines chat messages.\n\n"
            "RULES:\n"
            "- Return ONLY the refined message, nothing else\n"
            "- Keep it natural and human-like\n"
            "- Keep it concise — do not make messages longer than needed\n"
            "- Do not over-formalize casual conversations\n"
            "- Preserve any URLs, code snippets, or special formatting\n"
            "- If the message is very short (like 'ok', 'yes', 'lol'), return it as-is\n"
            "- Match the language of the original message\n"
        )
        return self

    def with_context(self, context: ConversationContext) -> PromptBuilder:
        if context.is_valid():
            self._user_parts.append(
                f"CONVERSATION CONTEXT ({context.app_name}"
                f"{', group chat' if context.is_group else ''}):\n"
                f"{context.format_for_prompt()}\n"
            )
        return self

    def with_draft(self, draft: str) -> PromptBuilder:
        is_reply = len(self._user_parts) > 0
        msg_type = "REPLY" if is_reply else "NEW MESSAGE"
        self._user_parts.append(f"DRAFT ({msg_type}):\n{draft}\n")
        return self

    def with_tone(self, tone: Tone) -> PromptBuilder:
        self._user_parts.append(f"TONE: {tone.label}\n{tone.instruction}\n")
        return self

    def with_constraints(self) -> PromptBuilder:
        self._user_parts.append(
            "TASK: Refine the draft message. Apply the tone. "
            "Fix grammar and spelling. Keep context in mind. "
            "Return ONLY the refined message."
        )
        return self

    def build(self) -> tuple[str, str]:
        """Returns (system_prompt, user_prompt)."""
        return self._system, "\n".join(self._user_parts)
