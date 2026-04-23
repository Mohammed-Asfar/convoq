"""Singleton ConfigManager — loads and provides access to application settings."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.yaml"
_USER_CONFIG_PATH = Path.home() / ".convoq" / "config.yaml"


class ConfigManager:
    """Singleton configuration manager.

    Loads defaults, overlays user config, and resolves env vars.
    """

    _instance: ConfigManager | None = None
    _data: dict[str, Any]

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        # Load defaults
        with open(_DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        # Overlay user config if exists
        if _USER_CONFIG_PATH.exists():
            with open(_USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                user_data = yaml.safe_load(f) or {}
            self._deep_merge(self._data, user_data)

        # Resolve env vars
        self._resolve_env_vars()

        logger.info("Config loaded (user config: %s)", _USER_CONFIG_PATH.exists())

    def _deep_merge(self, base: dict, overlay: dict) -> None:
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _resolve_env_vars(self) -> None:
        api_key = self._data.get("ai", {}).get("api_key", "")
        if not api_key:
            self._data.setdefault("ai", {})["api_key"] = os.environ.get("GROQ_API_KEY", "")

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Access nested config via dot notation: 'ai.model'"""
        keys = dotted_key.split(".")
        value = self._data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None
