"""
ZM Restaurant Recommendations — Streamlit app (Phase 7).

Run from repo root:
    streamlit run streamlit_app/app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo root on path for ``streamlit_app`` and optional ``backend``
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from streamlit_app.components.preference_form import (
    render_preference_form,
    render_status_sidebar,
)
from streamlit_app.components.results import (
    render_no_match,
    render_results,
    render_validation_errors,
)
from streamlit_app.service import NoMatchError, recommend
from zm.config import get_settings
from zm.data.pipeline import build_repository
from zm.data.repository import get_repository_holder
from zm.exceptions import ConfigurationError, DataLoadError, ValidationError


def _apply_streamlit_secrets() -> None:
    """Map Streamlit Cloud secrets into env for pydantic-settings."""
    try:
        secrets = st.secrets
    except Exception:
        return
    for key in (
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "DATASET_CACHE_DIR",
        "TOP_K_CANDIDATES",
        "DISPLAY_TOP_N",
        "HF_DATASET_ID",
    ):
        if key in secrets:
            os.environ[key] = str(secrets[key])
    get_settings.cache_clear()


@st.cache_resource
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
        page_title="ZM Restaurant Recommendations",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _apply_streamlit_secrets()
    settings = get_settings()

    st.title("ZM Restaurant Recommendations")
    st.markdown(
        "AI-powered picks from the Zomato dataset — structured filters plus "
        "Groq explanations. **Phase 7 — Streamlit deployment.**"
    )

    try:
        repo = load_repository()
        locations = repo.get_known_locations()
        data_error = None
    except (DataLoadError, ConfigurationError) as exc:
        repo = None
        locations = []
        data_error = str(exc)

    render_status_sidebar(
        {
            "restaurant_count": repo.count() if repo else 0,
            "groq_configured": settings.has_groq_api_key,
        }
    )

    if data_error:
        st.error(
            f"{data_error}\n\nRun `zm load-data` before deploying, or mount "
            "`data/cache` on Streamlit Cloud."
        )

    pref_input = render_preference_form(locations)
    if pref_input is None or repo is None:
        st.info("Set your preferences in the sidebar and click **Get recommendations**.")
        return

    with st.spinner("Searching and ranking restaurants…"):
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

    st.subheader("Recommendations")
    render_results(outcome)


if __name__ == "__main__":
    main()
