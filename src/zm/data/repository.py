"""In-memory restaurant repository (Phase 1)."""

from __future__ import annotations

import logging
import threading

from zm.models import Restaurant

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """Read-only in-memory store implementing ``RestaurantRepositoryPort``."""

    def __init__(self, restaurants: list[Restaurant]) -> None:
        self._by_id: dict[str, Restaurant] = {}
        self._by_location: dict[str, list[str]] = {}
        self._location_keys: dict[str, str] = {}

        for restaurant in restaurants:
            self._by_id[restaurant.id] = restaurant
            key = restaurant.location.casefold()
            self._location_keys.setdefault(key, restaurant.location)
            self._by_location.setdefault(key, []).append(restaurant.id)

        self._all_ids = list(self._by_id.keys())
        logger.info(
            "Repository ready: %s restaurants, %s locations",
            len(self._all_ids),
            len(self._by_location),
        )

    def is_ready(self) -> bool:
        return bool(self._by_id)

    def get_all(self) -> list[Restaurant]:
        return [self._by_id[rid] for rid in self._all_ids]

    def filter_by_location(self, location: str) -> list[Restaurant]:
        key = location.strip().casefold()
        if not key:
            return []
        ids = self._by_location.get(key, [])
        return [self._by_id[rid] for rid in ids]

    def get_known_locations(self) -> list[str]:
        return sorted(self._location_keys.values(), key=str.casefold)

    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        return self._by_id.get(restaurant_id)

    def count(self) -> int:
        return len(self._by_id)


class RepositoryHolder:
    """Thread-safe singleton holder for the active repository."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._repository: RestaurantRepository | None = None

    @property
    def repository(self) -> RestaurantRepository | None:
        return self._repository

    def set(self, repository: RestaurantRepository) -> None:
        with self._lock:
            self._repository = repository

    def get_or_raise(self) -> RestaurantRepository:
        repo = self.repository
        if repo is None or not repo.is_ready():
            raise RuntimeError(
                "Restaurant data is not loaded. Run `zm load-data` first."
            )
        return repo


# Process-wide holder used by CLI and future web app
_holder = RepositoryHolder()


def get_repository_holder() -> RepositoryHolder:
    return _holder
