"""
Phase 1 — data ingestion (separate package per architecture).

Load Zomato CSV from Hugging Face, normalize to ``Restaurant``, cache locally,
and query via ``RestaurantRepository``.
"""

from zm.data.pipeline import build_repository, ingest_from_csv
from zm.data.repository import (
    RepositoryHolder,
    RestaurantRepository,
    get_repository_holder,
)

__all__ = [
    "RestaurantRepository",
    "RepositoryHolder",
    "get_repository_holder",
    "build_repository",
    "ingest_from_csv",
]
