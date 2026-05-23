# ZM — AI-Powered Restaurant Recommendation

Zomato-inspired recommendation service combining structured restaurant data with an LLM.

**Current status:** Phases **0–7** — core library, REST API, **Next.js** frontend, Docker/hardening, and **Streamlit** deployment.

**Input channels:** **Next.js** (`frontend/` → `backend/` API) or **Streamlit** (`streamlit_app/`, in-process `zm`). The `zm` CLI is for developers only.

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

### Phase 1: Load restaurant data

```bash
zm load-data          # download CSV, normalize, write cache, load memory
zm load-data --force  # rebuild cache from Hugging Face
zm data-stats         # counts by city (after load-data)
```

Cached normalized data: `data/cache/restaurants_v1.jsonl`

### Phase 5–6: API + Next.js frontend (primary)

```bash
zm load-data    # required once
zm api          # REST API at http://127.0.0.1:8000/
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev     # http://localhost:3000/
```

Phase 6 adds **₹ budget for two** (maps to low/medium/high), **response caching**, **rate limiting**, **request IDs**, and **Docker Compose**:

```bash
docker compose up --build
```

API: http://localhost:8000 · Web: http://localhost:3000

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Liveness + data loaded |
| `GET /api/v1/locations` | Cities for dropdown |
| `GET /api/v1/metadata` | Budget bands, example cuisines |
| `POST /api/v1/recommendations` | Full pipeline → ranked JSON |

OpenAPI docs: `http://127.0.0.1:8000/docs`

### Phase 7: Streamlit deployment

Single-process UI for demos and [Streamlit Cloud](https://streamlit.io/cloud):

```bash
zm load-data
pip install -e ".[streamlit]"
zm streamlit    # http://localhost:8501/
```

See [streamlit_app/README.md](streamlit_app/README.md) for Cloud secrets and deploy steps.

### Phase 2 (legacy): Jinja web UI

```bash
zm serve        # http://127.0.0.1:8000/ — interim monolithic UI
```

### Phase 3: Integration (dev CLI)

```bash
zm candidates -l Bangalore -b medium -c "North Indian, Chinese" -r 4.0
zm candidates -l Bangalore -b medium -c Italian --json
```

### Phase 4: Groq recommendations

Set `GROQ_API_KEY` in `.env`, then:

```bash
zm recommend -l Bangalore -b medium -c "North Indian" -r 4.0
zm serve   # form submit runs full pipeline including Groq
```

Without `GROQ_API_KEY`, the app uses rule-based fallback rankings.

## Environment variables

Precedence: **environment variables override** `.env` file values (pydantic-settings default).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | For AI recommendations (Phase 4) | — | Groq API key ([console.groq.com](https://console.groq.com)) |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq chat model |
| `LLM_TIMEOUT_SECONDS` | No | `60` | Groq request timeout (seconds) |
| `HF_DATASET_ID` | No | `ManikaSaini/zomato-restaurant-recommendation` | Hugging Face dataset ID |
| `DATASET_CACHE_DIR` | No | `data/cache` | Local cache directory for dataset files |
| `TOP_K_CANDIDATES` | No | `25` | Max restaurants sent to the LLM (Phase 3+) |
| `DISPLAY_TOP_N` | No | `5` | Number of results shown to the user (Phase 5+) |
| `LOG_LEVEL` | No | `INFO` | Application log level |
| `WEB_HOST` | No | `127.0.0.1` | Bind address for API / web (Phase 5a+) |
| `WEB_PORT` | No | `8000` | Port for API / interim `zm serve` |
| `CORS_ORIGINS` | No | `http://localhost:3000,...` | Comma-separated origins for Next.js (Phase 5a/6) |
| `RECOMMENDATION_CACHE_TTL_SECONDS` | No | `300` | TTL for identical POST /recommendations (0 = off) |
| `RATE_LIMIT_PER_MINUTE` | No | `30` | Per-IP rate limit (0 = off) |

## Project layout

```
backend/             # Phase 5a — FastAPI REST API
frontend/            # Phase 5b/6 — Next.js App Router UI
streamlit_app/       # Phase 7 — Streamlit deployment
src/zm/              # Phases 0–4 — core library
├── config/          # Settings and environment loading
├── models/          # Restaurant, UserPreferences, Recommendation
├── data/            # Phase 1 — loader, normalizer, cache, repository
├── input/           # Phase 2 — validation
├── web/             # Interim Jinja UI (legacy)
├── integration/     # Phase 3 — filters, context, prompts
└── engine/          # Phase 4 — Groq client, parser, fallback
```

## Documentation

- [Problem statement](Docs/Problemstatement1.md)
- [Phase-wise architecture](Docs/PhaseWiseArchitecture.md)
- [Edge cases](Docs/EdgeCases.md)
- [Google Stitch UI prompt](Docs/GoogleStitch-UI-Prompt.md) — copy-paste prompt to generate the Next.js frontend UI
- [Streamlit deploy](streamlit_app/README.md) — Phase 7 hosting guide

## Development

```bash
pytest
zm --check
```
