"""RefinementPipeline — orchestrates the full refine flow."""

from __future__ import annotations

import logging
import time
import threading

from convoq.adapters.base import AppAdapter
from convoq.adapters.factory import AppAdapterFactory, UnsupportedAppError
from convoq.ai.groq_refiner import GroqRefiner
from convoq.ai.tone import Tone
from convoq.clipboard.manager import ClipboardManager
from convoq.config.config_manager import ConfigManager
from convoq.core.event_bus import EventBus, Events
from convoq.core.undo_manager import RefinementCommand, UndoManager
from convoq.models.context import ConversationContext

logger = logging.getLogger(__name__)


class RefinementPipeline:
    """Orchestrates: detect app → extract context → read draft → refine → replace.

    Subscribes to hotkey events via EventBus and runs refinement
    in a worker thread to keep the UI responsive.
    """

    def __init__(self) -> None:
        config = ConfigManager()
        self._refiner = GroqRefiner()
        self._undo = UndoManager()
        self._clipboard = ClipboardManager()
        self._passthrough_min = config.get("context.passthrough_min_chars", 3)
        self._running = False

    def start(self) -> None:
        EventBus.subscribe(Events.TONE_SELECTED, self._on_tone_selected)
        self._running = True
        logger.info("Refinement pipeline started")

    def stop(self) -> None:
        EventBus.unsubscribe(Events.TONE_SELECTED, self._on_tone_selected)
        self._running = False
        logger.info("Refinement pipeline stopped")

    def _on_tone_selected(self, tone: Tone) -> None:
        """Handle tone selection — run refinement in a background thread."""
        if not self._running:
            return
        thread = threading.Thread(target=self._refine, args=(tone,), daemon=True)
        thread.start()

    def _refine(self, tone: Tone) -> None:
        start_time = time.time()

        try:
            # 1. Detect active app and create adapter
            adapter = self._get_adapter()
            if adapter is None:
                return

            EventBus.emit(Events.REFINEMENT_STARTED, tone)

            # 2. Read draft from input field
            draft = adapter.get_draft()
            if not draft or not draft.strip():
                logger.info("Empty draft — skipping refinement")
                EventBus.emit(Events.REFINEMENT_FAILED, "Empty draft")
                return

            # 3. Passthrough threshold — don't refine very short messages
            if len(draft.strip()) < self._passthrough_min:
                logger.info("Draft too short (%d chars) — passing through", len(draft.strip()))
                EventBus.emit(Events.REFINEMENT_COMPLETED, draft)
                return

            # 4. Extract conversation context
            context = adapter.extract_context()

            # 5. Refine via AI
            refined = self._refiner.refine_sync(draft, context, tone)

            if not refined or not refined.strip():
                logger.warning("AI returned empty response — keeping original")
                EventBus.emit(Events.REFINEMENT_FAILED, "Empty AI response")
                return

            # 6. Replace text in the app
            adapter.replace_text(refined)

            # 7. Record for undo
            self._undo.record(RefinementCommand(
                original=draft,
                refined=refined,
                adapter=adapter,
                timestamp=time.time(),
            ))

            latency_ms = (time.time() - start_time) * 1000
            logger.info("Refinement complete (%.0fms): '%s' → '%s'", latency_ms, draft[:30], refined[:30])
            EventBus.emit(Events.REFINEMENT_COMPLETED, refined)

        except Exception as e:
            logger.exception("Refinement failed")
            EventBus.emit(Events.REFINEMENT_FAILED, str(e))

    def _get_adapter(self) -> AppAdapter | None:
        try:
            return AppAdapterFactory.create_for_active_window()
        except UnsupportedAppError as e:
            logger.warning("Unsupported app: %s", e)
            EventBus.emit(Events.REFINEMENT_FAILED, str(e))
            return None

    def undo(self) -> bool:
        return self._undo.undo_last()
