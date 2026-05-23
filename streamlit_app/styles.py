"""Global styles for Streamlit UI (Inter + ZM dark theme)."""

from __future__ import annotations

import streamlit as st

ZM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

.block-container {
  padding-top: 2rem;
  max-width: 1200px;
}

.zm-hero {
  margin-bottom: 1.5rem;
}
.zm-hero h1 {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.35rem 0;
  color: #e8edf4;
}
.zm-hero p {
  margin: 0;
  color: #8b9cb3;
  font-size: 1rem;
  line-height: 1.5;
}

.zm-panel {
  background: linear-gradient(145deg, rgba(26, 35, 50, 0.95), rgba(26, 35, 50, 0.75));
  border: 1px solid #2d3a4f;
  border-radius: 12px;
  padding: 1.25rem 1.35rem;
  margin-bottom: 1rem;
}
.zm-panel-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: #dee3ea;
  margin: 0 0 1rem 0;
}

.zm-card {
  background: #0f1419;
  border: 1px solid #2d3a4f;
  border-radius: 10px;
  padding: 1rem 1.1rem;
  margin-bottom: 0.75rem;
}
.zm-card-rank {
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 700;
  color: #3d9cf5;
  margin-bottom: 0.25rem;
}
.zm-card-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #e8edf4;
  margin: 0 0 0.75rem 0;
}
.zm-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.zm-meta dt {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #8b9cb3;
  margin: 0;
}
.zm-meta dd {
  font-size: 0.9rem;
  color: #dee3ea;
  margin: 0.15rem 0 0 0;
  font-weight: 500;
}
.zm-explanation {
  font-size: 0.9rem;
  line-height: 1.55;
  color: #c0c7d4;
  margin: 0;
}
.zm-explanation strong {
  color: #9fcaff;
  font-weight: 600;
}

div[data-testid="stForm"] {
  border: none;
  padding: 0;
}
div[data-testid="stFormSubmitButton"] > button {
  width: 100%;
  border-radius: 8px;
  font-weight: 600;
  padding: 0.65rem 1rem;
}
</style>
"""


def inject_styles() -> None:
    st.markdown(ZM_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    st.markdown(
        """
        <div class="zm-hero">
          <h1>ZM Restaurant Recommendations</h1>
          <p>AI-powered picks from real Zomato data — smart filters and Groq explanations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
