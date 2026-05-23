"""Zomato-style restaurant listing cards (Phase 7)."""

from __future__ import annotations

import html

import streamlit as st

from streamlit_app.service import RecommendOutcome
from streamlit_app.styles import card_placeholder_style


def _cuisine_tags(cuisines: list[str], rank: int) -> str:
    tags = [f'<span class="z-tag z-tag-rank">#{rank} pick</span>']
    for c in cuisines[:3]:
        tags.append(f'<span class="z-tag">{html.escape(c)}</span>')
    if len(cuisines) > 3:
        tags.append(f'<span class="z-tag">+{len(cuisines) - 3}</span>')
    return "".join(tags)


def _card_html(
    rank: int,
    name: str,
    cuisines: list[str],
    rating: str,
    rating_value: float | None,
    cost: str,
    explanation: str,
) -> str:
    img_style = card_placeholder_style(name)
    rating_class = "z-rating" if rating_value and rating_value >= 3.5 else "z-rating z-rating-muted"
    rating_display = f"★ {rating}" if rating != "N/A" else "New"
    cuisine_line = html.escape(", ".join(cuisines))

    return f"""
    <div class="z-card">
      <div class="z-card-img" style="{img_style}">🍴</div>
      <div class="z-card-body">
        <div class="z-card-top">
          <h3 class="z-card-name">{html.escape(name)}</h3>
          <span class="{rating_class}">{rating_display}</span>
        </div>
        <p class="z-cuisines">{cuisine_line}</p>
        <div class="z-tags">{_cuisine_tags(cuisines, rank)}</div>
        <p class="z-cost">{html.escape(cost)}</p>
        <p class="z-ai"><strong>Why we recommend</strong> — {html.escape(explanation)}</p>
      </div>
    </div>
    """


def render_results(outcome: RecommendOutcome) -> None:
    engine = outcome.engine
    count = len(engine.displays)
    source = "Groq AI" if engine.source == "groq" else "Smart ranking"

    st.markdown(
        f"""
        <div class="z-results-head">
          <h2 class="z-results-title">{count} restaurants for you</h2>
          <span class="z-badge">{html.escape(source)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if engine.result.summary:
        st.info(engine.result.summary)

    if engine.warning:
        st.warning(engine.warning)

    for item in engine.displays:
        rating_str = f"{item.rating:.1f}" if item.rating is not None else "N/A"
        st.markdown(
            _card_html(
                item.rank,
                item.name,
                item.cuisines,
                rating_str,
                item.rating,
                item.estimated_cost,
                item.explanation,
            ),
            unsafe_allow_html=True,
        )


def render_validation_errors(field_errors: dict[str, str]) -> None:
    st.error("Please check your filters")
    for field, msg in field_errors.items():
        st.markdown(f"**{field.replace('_', ' ').title()}** — {msg}")


def render_no_match(message: str) -> None:
    st.markdown(
        f"""
        <div class="z-empty">
          <div class="z-empty-icon">🔎</div>
          <p style="margin:0;font-weight:500;color:#1C1C1C;">No restaurants found</p>
          <p style="margin:0.5rem 0 0;font-size:0.9rem;">{html.escape(message)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_results() -> None:
    st.markdown(
        """
        <div class="z-empty">
          <div class="z-empty-icon">🍽️</div>
          <p style="margin:0;font-weight:500;color:#1C1C1C;">Hungry? Set your filters</p>
          <p style="margin:0.5rem 0 0;font-size:0.9rem;">
            Choose city, cuisine & budget — then hit <strong>Search restaurants</strong>.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
