"""Recommendation cards (Phase 7)."""

from __future__ import annotations

import html

import streamlit as st

from streamlit_app.service import RecommendOutcome


def _card_html(rank: int, name: str, cuisines: str, rating: str, cost: str, explanation: str) -> str:
    return f"""
    <div class="zm-card">
      <span class="zm-card-rank">#{rank}</span>
      <h3 class="zm-card-name">{html.escape(name)}</h3>
      <dl class="zm-meta">
        <div><dt>Cuisine</dt><dd>{html.escape(cuisines)}</dd></div>
        <div><dt>Rating</dt><dd>{html.escape(rating)}</dd></div>
        <div><dt>Cost</dt><dd>{html.escape(cost)}</dd></div>
      </dl>
      <p class="zm-explanation"><strong>Why this pick</strong><br/>{html.escape(explanation)}</p>
    </div>
    """


def render_results(outcome: RecommendOutcome) -> None:
    engine = outcome.engine

    if engine.result.summary:
        st.success(engine.result.summary)

    source_label = "Groq AI" if engine.source == "groq" else "Rule-based ranking"
    st.caption(f"Ranked by {source_label}")

    if engine.warning:
        st.warning(engine.warning)

    for item in engine.displays:
        rating = f"{item.rating:.1f}" if item.rating is not None else "N/A"
        cuisines = ", ".join(item.cuisines)
        st.markdown(
            _card_html(
                item.rank,
                item.name,
                cuisines,
                rating,
                item.estimated_cost,
                item.explanation,
            ),
            unsafe_allow_html=True,
        )


def render_validation_errors(field_errors: dict[str, str]) -> None:
    st.error("Please fix the errors below.")
    for field, msg in field_errors.items():
        st.markdown(f"**{field.replace('_', ' ').title()}** — {msg}")


def render_no_match(message: str) -> None:
    st.warning(message)


def render_empty_results() -> None:
    st.markdown(
        """
        <div class="zm-panel" style="text-align:center; color:#8b9cb3;">
          <p style="margin:0;">Submit the form to see ranked restaurants with AI explanations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
