from __future__ import annotations
from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, *, system_prompt: str, user_prompt: str, role: str) -> str:
        """Return model text. Implementations must not execute returned code."""
