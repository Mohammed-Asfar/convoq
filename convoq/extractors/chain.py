"""Chain of Responsibility — fallback chain for context extraction."""

from __future__ import annotations

import logging

from convoq.extractors.base import ContextExtractor, ExtractionError
from convoq.models.context import ConversationContext

logger = logging.getLogger(__name__)


class ExtractionChain:
    """Tries extractors in priority order, falling back on failure.

    Chain: UIAutomation → Accessibility → OCR → empty context
    """

    def __init__(self, extractors: list[ContextExtractor]) -> None:
        self._extractors = extractors

    def extract(self, app_name: str, window_handle: int | None = None) -> ConversationContext:
        for extractor in self._extractors:
            if not extractor.can_handle(app_name):
                continue
            try:
                result = extractor.extract(window_handle)
                if result.is_valid():
                    logger.info(
                        "Context extracted via %s (%d messages)",
                        type(extractor).__name__,
                        len(result.messages),
                    )
                    return result
            except ExtractionError as e:
                logger.warning(
                    "%s failed: %s — trying next extractor",
                    type(extractor).__name__,
                    e,
                )
            except Exception:
                logger.exception(
                    "%s raised unexpected error — trying next extractor",
                    type(extractor).__name__,
                )

        logger.warning("All extractors failed, returning empty context")
        return ConversationContext.empty()
