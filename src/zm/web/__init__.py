"""
Basic web UI — primary user input (Phase 2).

Run with ``zm serve`` or ``uvicorn zm.web.app:create_app --factory``.
"""

from zm.web.app import create_app, run_server

__all__ = ["create_app", "run_server"]
