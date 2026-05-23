# ZM — AI-Powered Restaurant Recommendation

Zomato-inspired recommendation service combining structured restaurant data with an LLM.

**Current status:** Phases **0–6** implemented locally; **Phase 7** production deploy on **Render** (API) + **Vercel** (Next.js UI).

**Input channel:** Next.js frontend → FastAPI backend. The `zm` CLI is for developers only.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -e ".[dev]"
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux

zm check
zm load-data
zm data-stats
```

### Local development (API + frontend)

```bash
zm load-data    # required once
zm api          # http://127.0.0.1:8000/
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev     # http://localhost:3000/
```

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Liveness + data loaded |
| `GET /api/v1/locations` | Cities for dropdown |
| `GET /api/v1/metadata` | Budget bands, example cuisines |
| `POST /api/v1/recommendations` | Full pipeline → ranked JSON |

OpenAPI: http://127.0.0.1:8000/docs

### Production deployment (Render + Vercel)

Step-by-step guide: **[Docs/Deployment-Render-Vercel.md](Docs/Deployment-Render-Vercel.md)**

| Service | Platform | Config |
|---------|----------|--------|
| Backend | [Render](https://render.com) | `render.yaml`, root `requirements.txt` |
| Frontend | [Vercel](https://vercel.com) | Root dir `frontend/`, `NEXT_PUBLIC_API_BASE_URL` |

### Docker (local / optional)

```bash
docker compose up --build
```

### Legacy Jinja UI

```bash
zm serve        # http://127.0.0.1:8000/ — interim monolithic UI
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | For AI (Render/local) | — | Groq API key |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq model |
| `CORS_ORIGINS` | Render prod | `http://localhost:3000,...` | Include your Vercel URL |
| `NEXT_PUBLIC_API_BASE_URL` | Vercel prod | — | Render API URL (see `frontend/.env.example`) |
| `DATASET_CACHE_DIR` | No | `data/cache` | Restaurant cache |
| `WEB_HOST` / `WEB_PORT` | No | `127.0.0.1` / `8000` | Local API bind |

See [.env.example](.env.example) for the full list.

## Project layout

```
backend/             # FastAPI REST API (Render)
frontend/            # Next.js App Router (Vercel)
render.yaml          # Render Blueprint
requirements.txt     # Python deps for Render
src/zm/              # Core library (Phases 0–4)
Docs/                # Architecture + deployment guides
```

## Documentation

- [Deployment: Render + Vercel](Docs/Deployment-Render-Vercel.md)
- [Phase-wise architecture](Docs/PhaseWiseArchitecture.md)
- [Problem statement](Docs/Problemstatement1.md)
- [Edge cases](Docs/EdgeCases.md)
- [Google Stitch UI prompt](Docs/GoogleStitch-UI-Prompt.md)

## Development

```bash
pytest
zm check
```
