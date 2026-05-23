"""Groq LLM client (Phase 4)."""

from __future__ import annotations

import logging
import time

from groq import Groq

from zm.config import Settings, get_settings
from zm.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class GroqLLMClient:
    """Chat completion client for Groq's OpenAI-compatible API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = Groq(
            api_key=self._settings.require_groq_api_key(),
            timeout=self._settings.llm_timeout_seconds,
        )

    @property
    def model(self) -> str:
        return self._settings.groq_model

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        """
        Send system + user messages to Groq and return assistant text.

        Retries once on transient failures (P4-01).
        """
        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
                if not content or not content.strip():
                    raise RuntimeError("Groq returned an empty completion")
                usage = getattr(response, "usage", None)
                if usage is not None:
                    logger.info(
                        "Groq completion model=%s prompt_tokens=%s completion_tokens=%s",
                        self.model,
                        getattr(usage, "prompt_tokens", "?"),
                        getattr(usage, "completion_tokens", "?"),
                    )
                return content.strip()
            except Exception as exc:
                last_error = exc
                logger.warning("Groq request failed (attempt %s): %s", attempt + 1, exc)
                if attempt == 0:
                    time.sleep(1.0)
        raise RuntimeError(f"Groq API request failed: {last_error}") from last_error


def create_groq_client(settings: Settings | None = None) -> GroqLLMClient:
    """Factory that validates configuration before creating the client."""
    settings = settings or get_settings()
    if not settings.has_groq_api_key:
        raise ConfigurationError(
            "GROQ_API_KEY is not set. Add it to your environment or .env file."
        )
    return GroqLLMClient(settings)
