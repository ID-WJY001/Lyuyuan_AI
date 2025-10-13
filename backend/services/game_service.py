from __future__ import annotations

"""Backend service wrapper that exposes the domain game core to routes.
This module is now the single source of truth (no legacy fallback).
"""

from backend.domain.game_core import game_core


class GameService:
    def __init__(self):
        self._core = game_core
        print("[BACKEND] game_service using backend.domain.game_core")

    def start_game(self, role=None):
        return self._core.start_new_game()

    def chat(self, message: str) -> str:
        return self._core.chat(message)

    def get_state(self):
        return self._core.get_current_state()

    def save(self, slot):
        return self._core.save_game(slot)

    def load(self, slot):
        return self._core.load_game(slot)


game_service = GameService()

__all__ = ["game_service", "GameService"]
