"""UI Automation extractor — uses pywinauto to read WhatsApp messages."""

from __future__ import annotations

import logging
import re

from convoq.config.config_manager import ConfigManager
from convoq.extractors.base import ContextExtractor, ExtractionError
from convoq.models.context import ConversationContext, Message

logger = logging.getLogger(__name__)


class UIAutomationExtractor(ContextExtractor):
    """Extracts conversation context from WhatsApp Desktop via pywinauto.

    Connects to the WhatsApp window, traverses the UI tree to find
    the message list, and parses the last N messages.
    """

    SUPPORTED_APPS = {"whatsapp"}

    def __init__(self) -> None:
        config = ConfigManager()
        self._max_messages = config.get("context.max_messages", 5)

    def can_handle(self, app_name: str) -> bool:
        return app_name.lower() in self.SUPPORTED_APPS

    def extract(self, window_handle: int | None = None) -> ConversationContext:
        try:
            from pywinauto import Desktop
        except ImportError as e:
            raise ExtractionError("pywinauto not installed") from e

        try:
            desktop = Desktop(backend="uia")
            whatsapp = desktop.window(title_re=".*WhatsApp.*")

            if not whatsapp.exists():
                raise ExtractionError("WhatsApp window not found")

            # Find the message list pane
            message_list = self._find_message_list(whatsapp)
            if message_list is None:
                raise ExtractionError("Could not locate message list in WhatsApp")

            messages = self._parse_messages(message_list)
            return ConversationContext(
                messages=tuple(messages[-self._max_messages :]),
                app_name="whatsapp",
                is_group=self._detect_group(whatsapp),
            )

        except ExtractionError:
            raise
        except Exception as e:
            raise ExtractionError(f"UI automation failed: {e}") from e

    def _find_message_list(self, window) -> object | None:
        """Traverse the UI tree to find the chat message list."""
        try:
            # WhatsApp Desktop typically has a ListView or a pane with message items
            children = window.children()
            for child in children:
                class_name = child.friendly_class_name()
                if "list" in class_name.lower() or "pane" in class_name.lower():
                    # Look for message-like children
                    sub_children = child.children()
                    if len(sub_children) > 2:
                        return child
            return None
        except Exception:
            return None

    def _parse_messages(self, message_list) -> list[Message]:
        """Parse individual message elements from the list."""
        messages: list[Message] = []
        try:
            items = message_list.children()
            for item in items:
                try:
                    text = item.window_text().strip()
                    if not text or len(text) < 2:
                        continue

                    sender = self._detect_sender(text, item)
                    messages.append(Message(text=text, sender=sender))
                except Exception:
                    continue
        except Exception:
            logger.warning("Failed to parse messages from list")

        return messages

    def _detect_sender(self, text: str, element) -> str:
        """Heuristic: detect if a message was sent by self or a contact."""
        try:
            # WhatsApp outgoing messages often have a specific automation ID or class
            automation_id = element.automation_id()
            if "out" in automation_id.lower() or "sent" in automation_id.lower():
                return "self"
        except Exception:
            pass
        return "contact"

    def _detect_group(self, window) -> bool:
        """Heuristic: detect if the current chat is a group."""
        try:
            title = window.window_text()
            # Group chats often show member count or multiple names
            if re.search(r"\d+ participants", title, re.IGNORECASE):
                return True
        except Exception:
            pass
        return False
