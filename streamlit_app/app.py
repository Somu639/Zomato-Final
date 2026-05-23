"""
ZM Restaurant Recommendations — Streamlit app (Phase 7).

Run from repo root:
    streamlit run streamlit_app/app.py
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
from streamlit_app.styles import inject_styles, render_hero
from zm.config import get_settings
from zm.data.pipeline import build_repository
from zm.data.repository import get_repository_holder
from zm.exceptions import ConfigurationError, DataLoadError, ValidationError


def _apply_streamlit_secrets() -> None:
    """Only deployment secrets — no model-tuning or load-limit overrides in the UI."""
    try:
        secrets = st.secrets
    except Exception:
        return
    for key in ("GROQ_API_KEY", "HF_DATASET_ID", "DATASET_CACHE_DIR"):
        if key in secrets:
            os.environ[key] = str(secrets[key])
    get_settings.cache_clear()


@st.cache_resource(show_spinner="Loading restaurant data…")
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
        page_title="ZM — Restaurant Recommendations",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    _apply_streamlit_secrets()
    settings = get_settings()
    render_hero()

    try:
        repo = load_repository()
        locations = repo.get_known_locations()
        data_error = None
    except (DataLoadError, ConfigurationError) as exc:
        repo = None
        locations = []
        data_error = str(exc)

    if data_error:
        st.error(
            f"{data_error}\n\nEnsure the Hugging Face dataset can be downloaded on first run."
        )

    col_form, col_results = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="zm-panel">', unsafe_allow_html=True)
        pref_input = render_preference_form(locations)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_results:
        st.markdown(
            '<p class="zm-panel-title">Recommendations</p>',
            unsafe_allow_html=True,
        )
        if pref_input is None or repo is None:
            render_empty_results()
            return

        with st.spinner("Finding the best matches…"):
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


if __name__ == "__main__":
    main()
