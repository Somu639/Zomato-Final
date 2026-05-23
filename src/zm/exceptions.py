"""Application-level exceptions."""


class ZMError(Exception):
    """Base exception for the ZM application."""


class ConfigurationError(ZMError):
    """Invalid or missing configuration (P0-01, P0-04)."""


class ValidationError(ZMError):
    """Invalid user input or domain data (Phase 2+)."""

    def __init__(
        self,
        message: str,
        *,
        field_errors: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.field_errors: dict[str, str] = field_errors or {}


class DataLoadError(ZMError):
    """Dataset download, parse, or cache failure (Phase 1)."""


class IntegrationError(ZMError):
    """Integration layer failure (Phase 3)."""
