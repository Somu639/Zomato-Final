"""Streamlit preference widgets (Phase 7)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from streamlit_app.service import PreferenceInput

BUDGET_BANDS = ["low", "medium", "high"]
EXAMPLE_CUISINES = "North Indian, Italian, Chinese"


def render_preference_form(locations: list[str]) -> PreferenceInput | None:
    with st.sidebar:
        st.header("Your preferences")
        if not locations:
            st.warning("Restaurant data is not loaded. Run `zm load-data` locally.")
            return None

        with st.form("preferences", clear_on_submit=False):
            location = st.selectbox(
                "City",
                options=[""] + locations,
                format_func=lambda x: "Select a city" if x == "" else x,
            )
            area = st.text_input("Area (optional)", placeholder="e.g. Bellandur")
            use_inr = st.checkbox("Budget in ₹ (for two)", value=True)
            if use_inr:
                budget_inr = st.number_input(
                    "Budget for two (₹)",
                    min_value=100,
                    max_value=50000,
                    value=2000,
                    step=100,
                )
                st.caption("≤₹600 low · ₹601–₹2000 medium · >₹2000 high")
                budget = None
            else:
                budget_inr = None
                budget = st.selectbox("Budget band", BUDGET_BANDS, index=1)
            cuisines = st.text_input(
                "Cuisines (comma-separated)",
                placeholder=EXAMPLE_CUISINES,
            )
            min_rating = st.slider("Minimum rating", 0.0, 5.0, 4.0, 0.1)
            additional = st.text_area(
                "Additional notes",
                placeholder="Ambiance, dietary needs…",
                height=80,
            )
            submitted = st.form_submit_button(
                "Get recommendations",
                type="primary",
                use_container_width=True,
            )

        if not submitted:
            return None

        if not location:
            st.error("location: Select a city")
            return None
        if not cuisines.strip():
            st.error("cuisines: Enter at least one cuisine")
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


def render_status_sidebar(extra: dict[str, Any] | None = None) -> None:
    with st.sidebar:
        st.divider()
        if not extra:
            return
        if extra.get("restaurant_count") is not None:
            st.caption(f"Restaurants loaded: {extra['restaurant_count']:,}")
        if extra.get("groq_configured") is not None:
            label = (
                "Groq configured"
                if extra["groq_configured"]
                else "Groq not set (rule-based fallback)"
            )
            st.caption(label)
