"""OCR fallback extractor — last resort when UI automation fails."""

from __future__ import annotations

import logging

from convoq.extractors.base import ContextExtractor, ExtractionError
from convoq.models.context import ConversationContext

logger = logging.getLogger(__name__)


class OCRExtractor(ContextExtractor):
    """Fallback extractor using screen capture + OCR.

    Placeholder for future implementation. Currently raises
    ExtractionError to allow the chain to fall through to empty context.
    """

    def can_handle(self, app_name: str) -> bool:
        # OCR can theoretically handle any app
        return True

    def extract(self, window_handle: int | None = None) -> ConversationContext:
        # TODO: Implement OCR-based extraction using Tesseract or Windows OCR API
        raise ExtractionError("OCR extractor not yet implemented")
