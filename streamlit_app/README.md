# Phase 7 — Streamlit deployment

Single-process UI for ZM restaurant recommendations. Calls the **`zm` Python core** in-process.

> This folder is named `streamlit_app/` (not `streamlit/`) to avoid clashing with the [Streamlit](https://streamlit.io) PyPI package.

## Local run

```bash
pip install -e .
python -m zm load-data
python -m zm streamlit
```

Open http://127.0.0.1:8501

## Secrets (local)

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` (gitignored):

```toml
GROQ_API_KEY = "your-key"
```

## Streamlit Community Cloud

1. Push repo to GitHub.
2. [Create app](https://streamlit.io/cloud) → **Main file:** `streamlit_app/app.py`
3. **Requirements:** root `requirements.txt` (`-e .` + `streamlit`)
4. **Secrets:** `GROQ_API_KEY` in app settings.

See [Docs/Deployment-Streamlit.md](../Docs/Deployment-Streamlit.md).

## Layout

```
streamlit_app/
├── app.py              # Entry
├── service.py          # validate → integrate → Groq
└── components/
    ├── preference_form.py
    └── results.py
```
