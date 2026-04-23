"""Command pattern — stores refinement history for undo support."""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field

from convoq.adapters.base import AppAdapter
from convoq.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


@dataclass
class RefinementCommand:
    """A recorded refinement that can be undone."""

    original: str
    refined: str
    adapter: AppAdapter
    timestamp: float = 0.0

    def undo(self) -> None:
        """Replace the refined text with the original."""
        logger.info("Undoing refinement: '%s' → '%s'", self.refined[:30], self.original[:30])
        self.adapter.replace_text(self.original)


class UndoManager:
    """Bounded stack of refinement commands for undo support.

    Keeps the last N refinements in a deque and can undo the most recent one.
    """

    def __init__(self) -> None:
        config = ConfigManager()
        max_history = config.get("undo.max_history", 10)
        self._history: deque[RefinementCommand] = deque(maxlen=max_history)

    def record(self, command: RefinementCommand) -> None:
        self._history.append(command)
        logger.debug("Recorded refinement (history size: %d)", len(self._history))

    def undo_last(self) -> bool:
        if self._history:
            command = self._history.pop()
            command.undo()
            return True
        logger.warning("Nothing to undo")
        return False

    @property
    def history_size(self) -> int:
        return len(self._history)
