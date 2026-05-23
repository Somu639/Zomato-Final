# Phase 7 — Streamlit deployment

Single-process UI for ZM restaurant recommendations. Calls the **`zm` Python core** in-process (no Next.js required).

> **Note:** This folder is named `streamlit_app/` (not `streamlit/`) to avoid clashing with the [Streamlit](https://streamlit.io) PyPI package on `import streamlit`.

## Local run

```bash
# From repo root
zm load-data
pip install -e ".[streamlit]"
streamlit run streamlit_app/app.py
```

Open http://localhost:8501

Or use the CLI:

```bash
zm streamlit
```

## Secrets (local)

Create `.streamlit/secrets.toml` (gitignored):

```toml
GROQ_API_KEY = "your-key"
```

## Streamlit Community Cloud

1. Push repo to GitHub (include `data/cache/restaurants_v1.jsonl` or run load on first deploy).
2. [Create app](https://streamlit.io/cloud) → **Main file:** `streamlit_app/app.py`
3. **Requirements:** `requirements-streamlit.txt` (or set `packages.txt` → that file).
4. **Secrets** (Settings → Secrets):

```toml
GROQ_API_KEY = "..."
# optional
GROQ_MODEL = "llama-3.3-70b-versatile"
DATASET_CACHE_DIR = "data/cache"
```

5. Deploy. Without `GROQ_API_KEY`, rankings use rule-based fallback.

## Optional: API-only mode

To point the UI at a remote FastAPI backend instead of in-process `zm`, set `ZM_API_URL` and extend `streamlit_app/service.py` (not enabled by default).

## Layout

```
streamlit_app/
├── app.py              # Entry
├── service.py          # validate → integrate → Groq
└── components/
    ├── preference_form.py
    └── results.py
```
