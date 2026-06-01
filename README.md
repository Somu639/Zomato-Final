# ZM — AI-Powered Restaurant Recommendation

Zomato-inspired recommendation service combining structured restaurant data with an LLM.

**Local dev:** FastAPI backend + Next.js frontend (no Streamlit required).

## Quick start (Windows)

Double-click **`run-dev.bat`** — opens backend and frontend in two windows.

Or manually in **two terminals**:

```powershell
# Terminal 1 — backend
cd c:\Users\din17512\Music\ZM
pip install -e .
python -m zm load-data          # first time only
python -m zm api                # http://127.0.0.1:8000  (/docs for API)

# Terminal 2 — frontend
cd c:\Users\din17512\Music\ZM\frontend
npm install                     # first time only
npm run dev                     # http://localhost:3000
```

Open **http://localhost:3000** in your browser.

The frontend proxies `/api/*` and `/health` to the backend via `frontend/next.config.ts`.

## Environment

Copy `.env.example` to `.env` and set `GROQ_API_KEY` (repo root — used by the backend).

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | For AI rankings | Groq API key |
| `DATASET_CACHE_DIR` | No | `data/cache` |

## Project layout

```
backend/             # FastAPI REST API (:8000)
frontend/            # Next.js UI (:3000)
src/zm/              # Core library
streamlit_app/       # Optional Streamlit UI (not used for local dev)
```

## Optional: Streamlit

Not needed for local dev. To run anyway: `python -m zm streamlit` → http://127.0.0.1:8501

## Development

```bash
pytest
python -m zm check
```
