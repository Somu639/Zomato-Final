"""Restaurant data source port (implemented in ``zm.data.repository``)."""

from typing import Protocol, runtime_checkable

from zm.models import Restaurant


@runtime_checkable
class RestaurantRepositoryPort(Protocol):
    """Read-only access to normalized restaurant records."""

    def is_ready(self) -> bool:
        """True when data has been loaded and queries are available."""
        ...

    def get_all(self) -> list[Restaurant]:
        """Return all restaurants (use sparingly; prefer filtered queries)."""
        ...

    def filter_by_location(self, location: str) -> list[Restaurant]:
        """Restaurants matching a city/area (case-insensitive after normalization)."""
        ...

    def get_known_locations(self) -> list[str]:
        """Distinct locations available for validation hints (Phase 2)."""
        ...

    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        """Lookup a single restaurant by stable id."""
        ...
