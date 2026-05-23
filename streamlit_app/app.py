"""
ZM / Zomato-style restaurant recommendations — Streamlit (Phase 7).
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
    try:
        secrets = st.secrets
    except Exception:
        return
    for key in ("GROQ_API_KEY", "HF_DATASET_ID", "DATASET_CACHE_DIR"):
        if key in secrets:
            os.environ[key] = str(secrets[key])
    get_settings.cache_clear()


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
    settings = get_settings()

    try:
        repo = load_repository()
        locations = repo.get_known_locations()
        data_error = None
    except (DataLoadError, ConfigurationError) as exc:
        repo = None
        locations = []
        data_error = str(exc)

    location_hint = locations[0] if locations else None
    render_header(location_hint)

    if data_error:
        st.error(data_error)

    col_filters, col_list = st.columns([5, 7], gap="medium")

    with col_filters:
        st.markdown('<div class="z-filter-box">', unsafe_allow_html=True)
        pref_input = render_preference_form(locations)
        st.markdown("</div>", unsafe_allow_html=True)

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


if __name__ == "__main__":
    main()
