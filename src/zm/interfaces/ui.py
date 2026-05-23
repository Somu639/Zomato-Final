"""Web UI port — primary user input (Phase 0 decision).

Implemented by the basic web UI in Phase 2 (preference form) and Phase 5
(results page). Not the CLI; see ``zm.cli`` for developer tooling only.
"""

from typing import Protocol, runtime_checkable

from zm.models import RecommendationDisplay, UserPreferences


@runtime_checkable
class UserInterfacePort(Protocol):
    """
    Browser-based UI: preference form input and recommendation display.

    Phase 2 wires the HTML form to ``UserPreferences``; Phase 5 renders
    ``RecommendationDisplay`` cards in the same web app.
    """

    def collect_preferences(self) -> UserPreferences:
        """Read and validate preferences submitted from the web form."""
        ...

    def display_results(
        self,
        results: list[RecommendationDisplay],
        *,
        summary: str | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        """Present enriched recommendations to the user."""
        ...

    def display_error(self, message: str) -> None:
        """Show a user-visible error (validation, config, no matches, etc.)."""
        ...

    def display_loading(self, message: str = "Finding recommendations…") -> None:
        """Optional loading indicator while the LLM runs."""
        ...
