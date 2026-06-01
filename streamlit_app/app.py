"""
ZM / Zomato-style restaurant recommendations — Streamlit (Phase 7).

Streamlit Cloud executes this file as a module (not __main__), so main() must run
unconditionally at the bottom — do not guard with if __name__ == "__main__".
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from streamlit_app.components.preference_form import render_preference_form
from streamlit_app.components.results import (
    render_empty_results,
    render_no_match,
    render_results,
    render_validation_errors,
)
from streamlit_app.service import NoMatchError, recommend
from streamlit_app.styles import inject_styles, render_header
from zm.config import get_settings
from zm.data.pipeline import build_repository
from zm.data.repository import get_repository_holder
from zm.exceptions import ConfigurationError, DataLoadError, ValidationError


def _apply_streamlit_secrets() -> None:
    """Load Streamlit Cloud secrets into os.environ when available."""
    try:
        from streamlit.errors import StreamlitSecretNotFoundError
    except ImportError:
        return

    try:
        secrets = st.secrets
        for key in ("GROQ_API_KEY", "HF_DATASET_ID", "DATASET_CACHE_DIR"):
            if key in secrets:
                os.environ[key] = str(secrets[key])
        get_settings.cache_clear()
    except StreamlitSecretNotFoundError:
        pass


@st.cache_resource(show_spinner="Loading restaurants…")
def load_repository():
    settings = get_settings()
    settings.ensure_cache_dir()
    holder = get_repository_holder()
    if holder.repository and holder.repository.is_ready():
        return holder.repository
    repo = build_repository(settings)
    holder.set(repo)
    return repo


def main() -> None:
    st.set_page_config(
        page_title="Zomatomate — Restaurant picks",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    _apply_streamlit_secrets()

    # Always paint the shell first so Cloud never shows a blank page while data loads.
    render_header(None)
    status = st.empty()
    status.info(
        "Loading restaurant data… First deploy on Streamlit Cloud can take 2–3 minutes."
    )

    settings = get_settings()
    repo = None
    locations: list[str] = []
    data_error: str | None = None

    try:
        repo = load_repository()
        locations = repo.get_known_locations()
        status.empty()
    except (DataLoadError, ConfigurationError) as exc:
        status.error(str(exc))
        data_error = str(exc)

    if locations:
        render_header(locations[0])

    if data_error:
        st.error(data_error)

    col_filters, col_list = st.columns([5, 7], gap="medium")

    with col_filters:
        with st.container(border=True):
            pref_input = render_preference_form(locations)

    with col_list:
        if pref_input is None or repo is None:
            render_empty_results()
            return

        with st.spinner("Finding the best restaurants near you…"):
            try:
                outcome = recommend(pref_input, repo, settings=settings)
            except ValidationError as exc:
                render_validation_errors(exc.field_errors)
                return
            except NoMatchError as exc:
                render_no_match(exc.message)
                return
            except ValueError as exc:
                st.error(str(exc))
                return

        render_results(outcome)


# Streamlit Cloud runs this script as a module — __name__ is not "__main__".
main()
