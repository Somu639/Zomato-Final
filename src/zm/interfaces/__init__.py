"""Abstract ports for swapping implementations and testing.

``UserInterfacePort`` is fulfilled by the basic web UI (primary input), not the CLI.
"""

from zm.interfaces.data_source import RestaurantRepositoryPort
from zm.interfaces.llm import LLMClientPort
from zm.interfaces.ui import UserInterfacePort

__all__ = [
    "RestaurantRepositoryPort",
    "LLMClientPort",
    "UserInterfacePort",
]
