"""Application configuration (Phase 0)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from zm.exceptions import ConfigurationError

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    """
    Application settings.

    Precedence: environment variables > .env file > defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str | None = Field(default=None, validation_alias="GROQ_API_KEY")
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias="GROQ_MODEL",
    )
    llm_timeout_seconds: int = Field(
        default=60, ge=1, validation_alias="LLM_TIMEOUT_SECONDS"
    )

    hf_dataset_id: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        validation_alias="HF_DATASET_ID",
    )
    dataset_cache_dir: Path = Field(
        default=Path("data/cache"),
        validation_alias="DATASET_CACHE_DIR",
    )

    top_k_candidates: int = Field(default=25, ge=1, le=100, validation_alias="TOP_K_CANDIDATES")
    display_top_n: int = Field(default=5, ge=1, le=20, validation_alias="DISPLAY_TOP_N")
    log_level: LogLevel = Field(default="INFO", validation_alias="LOG_LEVEL")

    web_host: str = Field(default="127.0.0.1", validation_alias="WEB_HOST")
    web_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        validation_alias=AliasChoices("PORT", "WEB_PORT"),
    )
    render: bool = Field(
        default=False,
        validation_alias=AliasChoices("RENDER", "IS_RENDER"),
    )
    cors_origins: str = Field(
        default=(
            "http://localhost:3000,http://127.0.0.1:3000,"
            "http://localhost:5173,http://127.0.0.1:5173"
        ),
        validation_alias="CORS_ORIGINS",
    )
    recommendation_cache_ttl_seconds: int = Field(
        default=300,
        ge=0,
        le=3600,
        validation_alias="RECOMMENDATION_CACHE_TTL_SECONDS",
    )
    rate_limit_per_minute: int = Field(
        default=30,
        ge=0,
        le=1000,
        validation_alias="RATE_LIMIT_PER_MINUTE",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parsed CORS allowlist for the React dev server (Phase 5a)."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_render(self) -> bool:
        """True when running on Render (``RENDER=true`` is set automatically)."""
        return self.render

    @property
    def has_only_local_cors_origins(self) -> bool:
        """True when every CORS origin is localhost (typical pre-Vercel setup)."""
        if not self.cors_origins_list:
            return True
        local_markers = ("localhost", "127.0.0.1")
        return all(
            any(marker in origin for marker in local_markers)
            for origin in self.cors_origins_list
        )

    @field_validator("groq_api_key", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def has_groq_api_key(self) -> bool:
        """True when a non-empty Groq API key is configured (P0-01, P0-02)."""
        return bool(self.groq_api_key and self.groq_api_key.strip())

    def require_groq_api_key(self) -> str:
        """Return Groq API key or raise ConfigurationError for Phase 4."""
        if not self.has_groq_api_key:
            raise ConfigurationError(
                "GROQ_API_KEY is not set. Add it to your environment or .env file."
            )
        return self.groq_api_key  # type: ignore[return-value]

    def ensure_cache_dir(self) -> Path:
        """
        Create cache directory if missing; verify writable (P0-03, P0-04).
        """
        path = self.dataset_cache_dir.resolve()
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ConfigurationError(
                f"Cannot create dataset cache directory: {path}"
            ) from exc

        probe = path / ".write_probe"
        try:
            probe.write_text("", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except OSError as exc:
            raise ConfigurationError(
                f"Dataset cache directory is not writable: {path}"
            ) from exc

        return path

    def redacted_summary(self) -> dict[str, object]:
        """Settings safe to log (no secrets)."""
        return {
            "groq_model": self.groq_model,
            "groq_configured": self.has_groq_api_key,
            "llm_timeout_seconds": self.llm_timeout_seconds,
            "hf_dataset_id": self.hf_dataset_id,
            "dataset_cache_dir": str(self.dataset_cache_dir),
            "top_k_candidates": self.top_k_candidates,
            "display_top_n": self.display_top_n,
            "log_level": self.log_level,
            "web_host": self.web_host,
            "web_port": self.web_port,
            "is_render": self.is_render,
            "cors_origins": self.cors_origins_list,
            "recommendation_cache_ttl_seconds": (
                self.recommendation_cache_ttl_seconds
            ),
            "rate_limit_per_minute": self.rate_limit_per_minute,
        }


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


def clear_settings_cache() -> None:
    """Reset cached settings (tests and config reload)."""
    get_settings.cache_clear()
