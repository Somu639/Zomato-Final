"""Render recommendation results (Phase 7)."""

from __future__ import annotations

import streamlit as st

from streamlit_app.service import RecommendOutcome


def render_results(outcome: RecommendOutcome) -> None:
    engine = outcome.engine
    stats = outcome.filter_stats

    if engine.result.summary:
        st.success(engine.result.summary)

    source_label = "Groq AI" if engine.source == "groq" else "Rule-based ranking"
    st.caption(
        f"Ranked by **{source_label}** · "
        f"Filtered {stats.location_count} → {stats.after_top_k} candidates"
    )

    if engine.warning:
        st.warning(engine.warning)

    for item in engine.displays:
        rating = f"{item.rating:.1f}" if item.rating is not None else "N/A"
        cuisines = ", ".join(item.cuisines)
        with st.expander(f"#{item.rank} · {item.name}", expanded=item.rank <= 3):
            col1, col2, col3 = st.columns(3)
            cuisine_label = cuisines[:40] + ("…" if len(cuisines) > 40 else "")
            col1.metric("Cuisine", cuisine_label)
            col2.metric("Rating", rating)
            col3.metric("Cost", item.estimated_cost)
            st.markdown("**Why this pick**")
            st.write(item.explanation)


def render_validation_errors(field_errors: dict[str, str]) -> None:
    st.error("Please fix the errors below.")
    for field, msg in field_errors.items():
        st.markdown(f"- **{field}:** {msg}")


def render_no_match(message: str) -> None:
    st.warning(message)
