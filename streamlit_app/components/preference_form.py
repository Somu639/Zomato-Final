"""Preference form — user-facing fields only (Phase 7)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.service import PreferenceInput

BUDGET_BANDS = ["low", "medium", "high"]
EXAMPLE_CUISINES = "North Indian, Italian, Chinese"


def render_preference_form(locations: list[str]) -> PreferenceInput | None:
    """Main-column form; no admin / model-tuning controls."""
    if not locations:
        st.warning(
            "Restaurant data is not loaded yet. On Streamlit Cloud, the app downloads "
            "the dataset on first startup — refresh in a minute. Locally, run `zm load-data`."
        )
        return None

    st.markdown('<p class="zm-panel-title">Your preferences</p>', unsafe_allow_html=True)

    with st.form("preferences", clear_on_submit=False):
        location = st.selectbox(
            "City",
            options=locations,
            index=0,
            help="Choose where you want to dine",
        )
        area = st.text_input(
            "Area (optional)",
            placeholder="e.g. Bellandur, Indiranagar",
        )
        cuisines = st.text_input(
            "Cuisines",
            placeholder=EXAMPLE_CUISINES,
            help="Comma-separated",
        )
        col_a, col_b = st.columns(2)
        with col_a:
            use_inr = st.checkbox("Budget in ₹ (for two)", value=True)
        with col_b:
            min_rating = st.slider(
                "Minimum rating",
                0.0,
                5.0,
                4.0,
                0.1,
                label_visibility="visible",
            )
        if use_inr:
            budget_inr = st.number_input(
                "Budget for two (₹)",
                min_value=100,
                max_value=50000,
                value=2000,
                step=100,
            )
            st.caption("≤₹600 · low  ·  ₹601–₹2000 · medium  ·  >₹2000 · high")
            budget = None
        else:
            budget_inr = None
            budget = st.selectbox("Budget band", BUDGET_BANDS, index=1)
        additional = st.text_area(
            "Additional notes",
            placeholder="Ambiance, dietary needs, occasion…",
            height=72,
        )
        submitted = st.form_submit_button(
            "Get recommendations",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None
    if not cuisines.strip():
        st.error("Enter at least one cuisine.")
        return None

    cuisine_list = [c.strip() for c in cuisines.split(",") if c.strip()]
    return PreferenceInput(
        location=location,
        cuisines=cuisine_list,
        min_rating=float(min_rating),
        budget=budget,
        budget_inr=int(budget_inr) if use_inr and budget_inr else None,
        additional=additional.strip() or None,
        area=area.strip() or None,
    )
