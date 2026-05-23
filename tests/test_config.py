import pytest

from zm.config.settings import Settings, clear_settings_cache
from zm.exceptions import ConfigurationError


def test_empty_groq_key_treated_as_missing(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "   ")
    settings = Settings()
    assert not settings.has_groq_api_key
    with pytest.raises(ConfigurationError):
        settings.require_groq_api_key()


def test_require_groq_api_key_when_set(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    settings = Settings()
    assert settings.require_groq_api_key() == "test-key"


def test_ensure_cache_dir_creates_path(tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    monkeypatch.setenv("DATASET_CACHE_DIR", str(cache))
    settings = Settings()
    resolved = settings.ensure_cache_dir()
    assert resolved.exists()
    assert resolved.is_dir()


def test_redacted_summary_never_includes_api_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "secret-key")
    settings = Settings()
    summary = settings.redacted_summary()
    assert "secret" not in str(summary).lower()
    assert summary["groq_configured"] is True
    assert summary["web_port"] == 8000


def test_web_bind_defaults(monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("WEB_PORT", raising=False)
    settings = Settings()
    assert settings.web_host == "127.0.0.1"
    assert settings.web_port == 8000


def test_port_env_overrides_web_port(monkeypatch):
    monkeypatch.setenv("PORT", "10000")
    monkeypatch.setenv("WEB_PORT", "8000")
    clear_settings_cache()
    settings = Settings()
    assert settings.web_port == 10000


def test_railway_detection(monkeypatch):
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")
    clear_settings_cache()
    settings = Settings()
    assert settings.is_railway is True
    assert settings.is_cloud_deploy is True
