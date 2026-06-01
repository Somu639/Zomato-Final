"""Zomato-inspired theme for Streamlit (Phase 7)."""

from __future__ import annotations

import hashlib

import streamlit as st

# Zomato brand palette
ZOMATO_RED = "#E23744"
ZOMATO_RED_DARK = "#CB202D"
BG_PAGE = "#F5F5F5"
BG_CARD = "#FFFFFF"
TEXT_PRIMARY = "#1C1C1C"
TEXT_SECONDARY = "#696B79"
TEXT_MUTED = "#9C9C9C"
BORDER = "#E8E8E8"
RATING_GREEN = "#24963F"
TAG_BG = "#F5F5F5"
AI_BG = "#FFF8F6"

ZOMATO_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: {TEXT_PRIMARY};
}}

.stApp {{
  background-color: {BG_PAGE};
}}

.block-container {{
  padding-top: 0;
  padding-bottom: 3rem;
  max-width: 1100px;
}}

/* Hide default Streamlit header padding */
header[data-testid="stHeader"] {{
  background: transparent;
}}

/* Primary button — Zomato red */
div[data-testid="stFormSubmitButton"] > button,
.stButton > button[kind="primary"] {{
  background-color: {ZOMATO_RED} !important;
  border: none !important;
  color: white !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(226, 55, 68, 0.35);
}}
div[data-testid="stFormSubmitButton"] > button:hover {{
  background-color: {ZOMATO_RED_DARK} !important;
}}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {{
  border-radius: 8px !important;
  border-color: {BORDER} !important;
}}
.stSlider > div > div > div {{
  background-color: {ZOMATO_RED} !important;
}}

/* Top bar — avoid negative margins that clip content on Cloud */
.z-header {{
  background: linear-gradient(135deg, {ZOMATO_RED} 0%, {ZOMATO_RED_DARK} 100%);
  margin: 0 0 1.5rem 0;
  padding: 1rem 1.5rem 1.25rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(226, 55, 68, 0.25);
}}
.z-logo {{
  font-size: 1.85rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
  margin: 0;
  line-height: 1;
}}
.z-logo span {{
  font-weight: 400;
  opacity: 0.95;
}}
.z-tagline {{
  color: rgba(255,255,255,0.9);
  font-size: 0.85rem;
  margin: 0.35rem 0 0 0;
  font-weight: 400;
}}

/* Filter panel */
.z-filter-box {{
  background: {BG_CARD};
  border-radius: 16px;
  padding: 1.25rem 1.35rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  border: 1px solid {BORDER};
  position: sticky;
  top: 1rem;
}}
.z-section-title {{
  font-size: 1rem;
  font-weight: 600;
  color: {TEXT_PRIMARY};
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}}
.z-section-sub {{
  font-size: 0.8rem;
  color: {TEXT_SECONDARY};
  margin: 0 0 1rem 0;
}}

/* Results header */
.z-results-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}}
.z-results-title {{
  font-size: 1.15rem;
  font-weight: 600;
  color: {TEXT_PRIMARY};
  margin: 0;
}}
.z-badge {{
  font-size: 0.75rem;
  font-weight: 500;
  color: {TEXT_SECONDARY};
  background: {BG_CARD};
  border: 1px solid {BORDER};
  padding: 0.25rem 0.65rem;
  border-radius: 20px;
}}

/* Restaurant card — Zomato listing style */
.z-card {{
  display: flex;
  gap: 1rem;
  background: {BG_CARD};
  border-radius: 16px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  border: 1px solid {BORDER};
  transition: box-shadow 0.2s ease;
}}
.z-card:hover {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}}
.z-card-img {{
  flex-shrink: 0;
  width: 88px;
  height: 88px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: rgba(255,255,255,0.9);
}}
.z-card-body {{
  flex: 1;
  min-width: 0;
}}
.z-card-top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}}
.z-card-name {{
  font-size: 1.05rem;
  font-weight: 600;
  color: {TEXT_PRIMARY};
  margin: 0;
  line-height: 1.3;
}}
.z-rating {{
  flex-shrink: 0;
  background: {RATING_GREEN};
  color: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  white-space: nowrap;
}}
.z-rating-muted {{
  background: {TEXT_MUTED};
}}
.z-cuisines {{
  font-size: 0.85rem;
  color: {TEXT_SECONDARY};
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}}
.z-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}}
.z-tag {{
  font-size: 0.72rem;
  font-weight: 500;
  color: {TEXT_SECONDARY};
  background: {TAG_BG};
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  border: 1px solid {BORDER};
}}
.z-tag-rank {{
  background: #FFF0F1;
  color: {ZOMATO_RED};
  border-color: #FFD4D8;
  font-weight: 600;
}}
.z-cost {{
  font-size: 0.85rem;
  color: {TEXT_PRIMARY};
  font-weight: 500;
  margin-bottom: 0.5rem;
}}
.z-ai {{
  font-size: 0.82rem;
  line-height: 1.5;
  color: {TEXT_SECONDARY};
  background: {AI_BG};
  border-left: 3px solid {ZOMATO_RED};
  padding: 0.5rem 0.65rem;
  border-radius: 0 8px 8px 0;
  margin: 0;
}}
.z-ai strong {{
  color: {ZOMATO_RED};
  font-weight: 600;
}}

.z-empty {{
  text-align: center;
  padding: 3rem 1.5rem;
  background: {BG_CARD};
  border-radius: 16px;
  border: 1px dashed {BORDER};
  color: {TEXT_SECONDARY};
}}
.z-empty-icon {{
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}}

div[data-testid="stForm"] {{
  border: none;
  padding: 0;
}}
</style>
"""


def inject_styles() -> None:
    st.markdown(ZOMATO_CSS, unsafe_allow_html=True)


def card_placeholder_style(name: str) -> str:
    """Deterministic accent color per restaurant (image placeholder)."""
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    hue = int(digest[:2], 16) % 360
    return f"background: linear-gradient(135deg, hsl({hue}, 55%, 42%), hsl({(hue + 40) % 360}, 50%, 32%));"


def render_header(location_hint: str | None = None) -> None:
    loc = html_escape(location_hint) if location_hint else "Discover restaurants"
    st.markdown(
        f"""
        <div class="z-header">
          <p class="z-logo">zomato<span>mate</span></p>
          <p class="z-tagline">{loc} · AI picks powered by Groq</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def html_escape(text: str) -> str:
    import html

    return html.escape(text)
