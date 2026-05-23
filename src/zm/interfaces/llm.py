"""LLM recommendation port (implemented by ``zm.engine.groq_client.GroqLLMClient``)."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClientPort(Protocol):
    """Groq chat completion for Phase 4 ranking."""

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """Return raw assistant message text (expected JSON)."""
        ...
