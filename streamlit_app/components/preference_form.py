"""Zomato-style filter form (Phase 7)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.service import PreferenceInput

BUDGET_BANDS = ["low", "medium", "high"]
EXAMPLE_CUISINES = "North Indian, Biryani, Chinese"


def render_preference_form(locations: list[str]) -> PreferenceInput | None:
    if not locations:
        st.warning(
            "Loading restaurants… Refresh shortly, or run `zm load-data` locally."
        )
        return None

    st.markdown(
        """
        <p class="z-section-title">🔍 Find restaurants</p>
        <p class="z-section-sub">Set filters like on Zomato — we’ll rank matches for you.</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("preferences", clear_on_submit=False):
        location = st.selectbox(
            "📍 City",
            options=locations,
            index=0,
        )
        area = st.text_input(
            "Neighbourhood",
            placeholder="Search area, e.g. Bellandur",
        )
        cuisines = st.text_input(
            "🍽️ Cuisine",
            placeholder=EXAMPLE_CUISINES,
        )
        st.markdown(
            '<p style="font-size:0.8rem;color:#696B79;margin:0.5rem 0 0.25rem;">Budget & rating</p>',
            unsafe_allow_html=True,
        )
        use_inr = st.checkbox("Use budget for two (₹)", value=True)
        if use_inr:
            budget_inr = st.number_input(
                "₹ for two",
                min_value=100,
                max_value=50000,
                value=2000,
                step=100,
                label_visibility="collapsed",
            )
            st.caption("Budget bands: ≤₹600 · ₹601–2k · ₹2k+")
            budget = None
        else:
            budget_inr = None
            budget = st.selectbox(
                "Price range",
                BUDGET_BANDS,
                index=1,
                format_func=lambda x: {"low": "₹ Budget", "medium": "₹₹ Mid", "high": "₹₹₹ Premium"}[x],
            )
        min_rating = st.slider(
            "Minimum rating",
            0.0,
            5.0,
            4.0,
            0.1,
        )
        additional = st.text_area(
            "More filters",
            placeholder="Family-friendly, outdoor seating…",
            height=68,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button(
            "Search restaurants",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return None
    if not cuisines.strip():
        st.error("Add at least one cuisine to search.")
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
