from __future__ import annotations

import os
import secrets
from typing import Optional


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    val = os.environ.get(name)
    try:
        return int(val) if val is not None else default
    except Exception:
        return default


# Secret key for Flask session
SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# Server network settings
HOST: str = os.environ.get("HOST", "0.0.0.0")
PORT: int = _get_int("PORT", 8080)
DEBUG: bool = _get_bool("DEBUG", False)

# LLM Provider settings
LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "deepseek").lower()
LLM_MODEL: Optional[str] = os.environ.get("LLM_MODEL")  # None = use provider default
LLM_TEMPERATURE: float = float(os.environ.get("LLM_TEMPERATURE", "0.8"))
LLM_MAX_TOKENS: int = _get_int("LLM_MAX_TOKENS", 1500)
LLM_TIMEOUT: int = _get_int("LLM_TIMEOUT", 45)


# Expose selected config for imports
__all__ = [
    "SECRET_KEY",
    "HOST",
    "PORT",
    "DEBUG",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_TEMPERATURE",
    "LLM_MAX_TOKENS",
    "LLM_TIMEOUT",
]
