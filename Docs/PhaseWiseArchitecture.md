# Phase-Wise Architecture: AI-Powered Restaurant Recommendation System

This document defines a phased architecture for the system described in [Problemstatement1.md](./Problemstatement1.md). Phases **0–4** are implemented in the Python core (`src/zm/`). **Phase 5** introduces a **backend + frontend** split; **Phase 6** adds production hardening; **Phase 7** is **cloud deployment** on **Railway** (API) and **Vercel** (Next.js UI).

---

## System Architecture (Post Phase 5)

### Target: separated backend and frontend

```mermaid
flowchart TB
    subgraph FE["Frontend (Phase 5b)"]
        UI[React SPA]
        FORM[Preference Form]
        CARDS[Recommendation Cards]
        UI --> FORM
        UI --> CARDS
    end

    subgraph BE["Backend API (Phase 5a)"]
        API[FastAPI REST]
        SVC[Recommendation Service]
        DTO[API Schemas / DTOs]
        API --> SVC --> DTO
    end

    subgraph CORE["Python Core (Phases 0–4)"]
        INPUT[input]
        DATA[data]
        INT[integration]
        ENG[engine / Groq]
        PRES[presentation]
        INPUT --> INT
        DATA --> INT
        INT --> ENG
        ENG --> PRES
    end

    subgraph EXT["External"]
        GROQ[Groq API]
        HF[Hugging Face Dataset]
    end

    FORM -->|HTTPS JSON| API
    CARDS -->|HTTPS JSON| API
    SVC --> INPUT
    SVC --> DATA
    SVC --> INT
    SVC --> ENG
    SVC --> PRES
    ENG --> GROQ
    DATA --> HF
```

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| **Frontend** | Next.js + TypeScript (App Router) | UX only: forms, validation display, results, loading/errors |
| **Backend API** | FastAPI | HTTP routes, CORS, request/response mapping, orchestration |
| **Core library** | `zm` Python package | Business logic: data, validation, filters, Groq, enrichment |
| **Data store** | JSONL cache + in-memory repository | Restaurant catalog (Phase 1) |

**Core principle:** Structured data narrows the search space; Groq reasons over a small candidate set. The frontend never calls Groq or reads the dataset directly.

---

## High-Level Phase Flow (Logical)

```mermaid
flowchart LR
    subgraph P1["Phase 1: Data"]
        HF[Hugging Face Dataset]
        ETL[Load & Preprocess]
        STORE[(Restaurant Store)]
        HF --> ETL --> STORE
    end

    subgraph P2["Phase 2: Input"]
        VALID[Validation Layer]
    end

    subgraph P3["Phase 3: Integration"]
        FILTER[Filter & Top-K]
        CTX[LLM Context]
        FILTER --> CTX
    end

    subgraph P4["Phase 4: Engine"]
        GROQ[Groq LLM]
        PARSE[Parser + Fallback]
        GROQ --> PARSE
    end

    subgraph P5["Phase 5: Delivery"]
        API[Backend API]
        SPA[Frontend SPA]
        API <--> SPA
    end

    VALID --> FILTER
    STORE --> FILTER
    CTX --> GROQ
    PARSE --> API
```

---

## Phase Overview

| Phase | Name | Primary outcome | Depends on |
|-------|------|-----------------|------------|
| 0 | Foundation | Repo, config, contracts | — |
| 1 | Data ingestion | Clean restaurant records in repository | Phase 0 |
| 2 | User input | Validated `UserPreferences` | Phase 0 |
| 3 | Integration layer | Filtered candidates + LLM context | Phases 1, 2 |
| 4 | Recommendation engine | Groq-ranked list + explanations | Phase 3 |
| 5a | Backend API | REST API orchestrating core | Phases 1–4 |
| 5b | Frontend | SPA consuming REST API | Phase 5a |
| 6 | Hardening (optional) | Docker, cache, observability | Phases 1–5 |
| 7 | Cloud deployment | Railway (API) + Vercel (frontend) | Phases 5a, 5b, 6 |

**Current implementation status**

| Phase | Status | Location |
|-------|--------|----------|
| 0–4 | Implemented | `src/zm/` |
| 5a | Implemented | `backend/` — FastAPI REST API |
| 5b | Implemented | `frontend/` — Next.js (Vercel) |
| 6 | Implemented | Docker Compose, cache, rate limits, observability, INR budget |
| 7 | Implemented | [Deployment-Railway-Vercel.md](./Deployment-Railway-Vercel.md), `railway.toml`, `backend/startup.py` |
| 5 (interim / legacy) | Available | `src/zm/web/` (monolithic FastAPI + Jinja, `zm serve`) |

---

## Phase 0: Foundation

**Goal:** Establish project structure, configuration, and shared contracts so later phases integrate without rework.

### Components

| Component | Responsibility |
|-----------|----------------|
| Project scaffold | Python package `zm`, dependency management |
| Configuration | `GROQ_API_KEY`, dataset cache, API/frontend URLs |
| Domain models | `Restaurant`, `UserPreferences`, `Recommendation`, `RecommendationDisplay` |
| Interfaces | Ports for data source, LLM completer, UI (for tests) |

### Deliverables

- Shared types in `src/zm/models/`
- Documented env vars (see [README](../README.md))
- No UI framework locked in Phase 0 (API + SPA decided in Phase 5)

### Exit criteria

- Phases 1–5a import the same models without circular dependencies

---

## Phase 1: Data Ingestion

**Goal:** Load the Zomato dataset from Hugging Face, normalize it, and expose queryable restaurant records.

*Maps to problem statement: **§1 Data Ingestion***

| Component | Responsibility |
|-----------|----------------|
| Dataset loader | Download `zomato.csv` via Hugging Face Hub |
| Preprocessor | Dedupe, skip invalid rows |
| Field normalizer | Map CSV → `Restaurant` |
| Restaurant repository | `filter_by_location()`, `get_known_locations()`, `get_by_id()` |

**Package:** `src/zm/data/`

### Exit criteria

- ≥1 city returns a non-empty restaurant set
- `zm load-data` builds `data/cache/restaurants_v1.jsonl`

---

## Phase 2: User Input

**Goal:** Collect and validate user preferences before any recommendation runs.

*Maps to problem statement: **§2 User Input***

| Component | Responsibility |
|-----------|----------------|
| Validation layer | `validate_form()` / `validate_json()` → `UserPreferences` |
| Location matcher | Known cities + fuzzy suggestions |
| API schemas | `PreferenceFormInput`, error responses |

**Package:** `src/zm/input/`

### Preference schema

| Field | Type | Validation |
|-------|------|------------|
| `location` | string | Required; known city (e.g. Bangalore); area via `additional` |
| `budget` | enum | `low` \| `medium` \| `high` (numeric budget mapped in UI/API) |
| `cuisine` | string or list | At least one cuisine |
| `min_rating` | float | 0–5 |
| `additional` | string | Optional; area (e.g. Bellandur), free-text prefs, max 500 chars |

### Exit criteria

- Invalid input never reaches filter or Groq
- Same validation used by backend API and frontend (server-side authority)

---

## Phase 3: Integration Layer

**Goal:** Reduce the dataset to a relevant candidate set and build LLM-ready context.

*Maps to problem statement: **§3 Integration Layer***

| Component | Responsibility |
|-----------|----------------|
| Hard filters | Location (city), min rating, cuisine OR-match, budget band |
| Soft scoring | Rank by rating + budget fit before Top-K |
| Context packager | JSON with `restaurant_id`, name, cuisine, rating, cost |
| Prompt templates v1 | System + user prompts for Groq |

**Package:** `src/zm/integration/`

### Exit criteria

- Typical query returns 10–30 candidates in &lt;100ms (local data)
- Zero candidates → clear message, **no Groq call**

---

## Phase 4: Recommendation Engine (Groq)

**Goal:** Use **Groq** to rank candidates, explain fit, and optionally summarize.

*Maps to problem statement: **§4 Recommendation Engine***

| Component | Responsibility |
|-----------|----------------|
| Groq client | `llama-3.3-70b-versatile` (configurable), JSON mode, retry |
| Parser | Strip fences, validate IDs against candidates |
| Fallback | Rule-based Top-N if Groq fails or key missing |
| Enricher | `RecommendationDisplay` for UI/API |

**Package:** `src/zm/engine/`

### LLM provider

| Setting | Default |
|---------|---------|
| `GROQ_API_KEY` | Required for AI rankings |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |

### LLM output schema

```json
{
  "summary": "Optional one-line overview",
  "recommendations": [
    {
      "restaurant_id": "string",
      "rank": 1,
      "explanation": "Why this matches location, budget, cuisine, and extras"
    }
  ]
}
```

### Exit criteria

- Top N results include explanations grounded in preferences
- Hallucinated `restaurant_id` values are dropped (P4-16)

---

## Phase 5: Backend + Frontend (Target Architecture)

**Goal:** Deliver the product through a **proper REST backend** and a **dedicated frontend SPA**, replacing the interim monolithic `zm/web` template app.

*Maps to problem statement: **§2 User Input** and **§5 Output Display***

---

### Phase 5a: Backend API

**Goal:** Thin HTTP layer that orchestrates the Python core and exposes stable JSON contracts.

#### Components

```mermaid
flowchart TB
    subgraph API["backend/"]
        ROUTES[api/routes]
        SCHEMAS[api/schemas]
        SVC[services/recommendation_service]
        DEPS[api/deps]
        MAIN[main.py]
    end

    subgraph CORE["src/zm/"]
        REC[engine.recommend]
        VAL[input.validator]
        REPO[data.repository]
    end

    ROUTES --> SVC
    SVC --> VAL
    SVC --> REC
    DEPS --> REPO
    MAIN --> ROUTES
```

| Component | Responsibility |
|-----------|----------------|
| `main.py` | FastAPI app, CORS, lifespan (load dataset on startup) |
| Routes | REST endpoints (see below) |
| Service layer | `RecommendationService.recommend()` — single orchestration entry |
| API schemas | Pydantic DTOs mirroring frontend types (decoupled from domain if needed) |
| Dependencies | Repository holder, settings injection |
| Error mapping | 400 validation, 404 no matches, 503 data not loaded, 502 Groq degraded |

#### REST API contract

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness + data loaded flag |
| `GET` | `/api/v1/locations` | Known cities for dropdown |
| `GET` | `/api/v1/metadata` | Budget bands, example cuisines |
| `POST` | `/api/v1/recommendations` | Full pipeline → ranked results |

**`POST /api/v1/recommendations` request body**

```json
{
  "location": "Bangalore",
  "budget": "high",
  "cuisines": ["North Indian", "Italian"],
  "min_rating": 4.0,
  "additional": "Prefer Bellandur area. Budget around 2000 for two."
}
```

**Success response (`200`)**

```json
{
  "ok": true,
  "source": "groq",
  "warning": null,
  "summary": "Top picks in Bellandur matching your budget",
  "preferences": { "location": "Bangalore", "budget": "high", "cuisines": ["North Indian", "Italian"], "min_rating": 4.0 },
  "filter_stats": { "location_count": 362, "after_budget": 16, "after_top_k": 16 },
  "recommendations": [
    {
      "restaurant_id": "abc123",
      "rank": 1,
      "name": "MoMo Cafe - Courtyard by Marriott",
      "cuisines": ["Asian", "North Indian"],
      "rating": 4.2,
      "estimated_cost": "₹2,000 for two",
      "explanation": "..."
    }
  ]
}
```

**Error response (`422`)**

```json
{
  "ok": false,
  "errors": { "location": "Did you mean Bangalore?" },
  "message": "Please fix the errors below."
}
```

#### Suggested backend layout

```
backend/
├── main.py                 # FastAPI entry, CORS, mount routes
├── api/
│   ├── routes/
│   │   ├── health.py
│   │   └── recommendations.py
│   ├── schemas.py          # Request/response DTOs
│   └── deps.py             # get_repository, get_settings
└── services/
    └── recommendation_service.py   # calls zm.engine.recommend
```

**Core stays in** `src/zm/` — backend imports `zm` as a library (no business logic duplication).

#### Deliverables

- OpenAPI docs at `/docs`
- CORS configured for frontend origin (e.g. `http://localhost:3000`)
- Startup loads restaurant cache (same as `zm load-data`)

#### Exit criteria

- Frontend can complete full flow using only REST (no server-rendered HTML)
- All five display fields served from JSON per result

---

### Phase 5b: Frontend

**Goal:** Modern SPA for preference input and recommendation display.

#### Components

```mermaid
flowchart LR
    subgraph FE["frontend/"]
        APP[App shell]
        PAGE[RecommendPage]
        FORM[PreferenceForm]
        LIST[RecommendationList]
        API_CLIENT[api/client.ts]
    end

    APP --> PAGE
    PAGE --> FORM
    PAGE --> LIST
    FORM --> API_CLIENT
    LIST --> API_CLIENT
    API_CLIENT -->|fetch| BE[Backend :8000]
```

| Component | Responsibility |
|-----------|----------------|
| Preference form | Location select, budget, cuisines, rating, additional notes |
| API client | `POST /api/v1/recommendations`, typed errors |
| Results view | Cards: name, cuisine, rating, cost, AI explanation, rank |
| UX states | Loading spinner, field errors, empty/no-match, Groq fallback banner |
| Config | `VITE_API_BASE_URL` → backend |

#### Suggested frontend layout

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── RecommendPage.tsx
│   ├── PreferenceForm.tsx
│   └── ...
├── lib/api/
│   ├── client.ts
│   └── types.ts
├── next.config.ts           # rewrites /api → backend
└── package.json
```

#### UI requirements (problem statement §5)

| Field | Source |
|-------|--------|
| Restaurant name | API / dataset |
| Cuisine | API |
| Rating | API |
| Estimated cost | API |
| AI explanation | Groq (via API) |

#### Deliverables

- Responsive layout (mobile-friendly cards)
- No secrets in frontend (Groq key server-side only)

#### Exit criteria

- User completes flow in browser without CLI or Jinja templates
- Works against backend on localhost (dev) and deployed URL (prod)

---

### Interim MVP (current)

Until Phase 5a/5b are complete, **`src/zm/web/`** provides:

- `GET /` — Jinja form
- `POST /recommendations` — form POST + inline HTML results
- `POST /api/preferences` — partial JSON API

This monolith **implements the same orchestration** as the target backend but mixes presentation and API. Migrate routes to `backend/` and UI to `frontend/` without changing `src/zm/` core logic.

---

## Phase 6: Hardening (Optional)

| Area | Examples |
|------|----------|
| Deployment | Docker Compose: `api` + `web` + volume for `data/cache` |
| Caching | Short TTL cache for identical recommendation requests |
| Observability | Request ID, phase timings, Groq token/latency logs |
| Security | CORS allowlist, rate limits, no API keys in frontend |
| Area filter | First-class Bellandur / area filter in integration |
| Budget UX | Numeric budget (₹2000) mapped to band in API layer |

---

## Phase 7: Cloud deployment (Railway + Vercel)

**Goal:** Host the production stack as two managed services: **FastAPI on Railway**, **Next.js on Vercel**. No Streamlit in the deployment path.

**Full runbook:** [Deployment-Railway-Vercel.md](./Deployment-Railway-Vercel.md)

### Architecture

```mermaid
flowchart LR
    User[User]
    Vercel[Vercel — Next.js]
    Railway[Railway — FastAPI]
    Groq[Groq]
    HF[Hugging Face]

    User --> Vercel
    Vercel -->|HTTPS /api/v1| Railway
    Railway --> Groq
    Railway --> HF
```

| Service | Platform | Repo path | Start / build |
|---------|----------|-----------|----------------|
| **Backend** | Railway | repo root | Build: `pip install -e .` · Start: `uvicorn backend.main:create_app --factory --host 0.0.0.0 --port $PORT` |
| **Frontend** | Vercel | `frontend/` | `npm run build` · env: `NEXT_PUBLIC_API_BASE_URL` |

### Repo artifacts

| File | Purpose |
|------|---------|
| `railway.toml` | Railway config-as-code |
| `Procfile` | Start command for Nixpacks |
| `nixpacks.toml` | Python 3.11 + install steps |
| `requirements.txt` | Python deps for Railway (`-e .`) |
| `frontend/vercel.json` | Vercel project hints |
| `frontend/.env.example` | `NEXT_PUBLIC_API_BASE_URL` template |

### Secrets

| Secret | Where |
|--------|--------|
| `GROQ_API_KEY` | Railway only |
| `CORS_ORIGINS` | Railway (Vercel production URL) |
| `NEXT_PUBLIC_API_BASE_URL` | Vercel (Railway API URL) |

### Exit criteria

- Vercel UI loads cities from Railway `/api/v1/locations`
- Full recommend flow works with CORS configured
- `GROQ_API_KEY` never present in frontend bundle or Vercel env

---

## End-to-End Request Flow (Post Phase 5)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend SPA
    participant API as Backend API
    participant SVC as RecommendationService
    participant CORE as zm core
    participant GROQ as Groq

    U->>FE: Fill preference form
    FE->>API: POST /api/v1/recommendations
    API->>SVC: recommend(dto)
    SVC->>CORE: validate → integrate → engine
    CORE->>GROQ: chat completion
    GROQ-->>CORE: JSON rankings
    CORE-->>SVC: EngineResult + displays
    SVC-->>API: Response DTO
    API-->>FE: 200 JSON
    FE-->>U: Render recommendation cards
```

---

## Repository Layout (Target)

```
ZM/
├── railway.toml             # Phase 7 — Railway config
├── Procfile                 # Phase 7 — Railway start command
├── requirements.txt         # Railway pip install
├── backend/                 # Phase 5a — FastAPI REST API
│   ├── main.py
│   ├── api/
│   └── services/
├── frontend/                # Phase 5b / 6 — Next.js UI
│   ├── app/
│   └── package.json
├── nixpacks.toml            # Phase 7 — Nixpacks (Python 3.11)
├── src/zm/                  # Phases 0–4 core (library)
│   ├── config/
│   ├── models/
│   ├── data/                # Phase 1
│   ├── input/               # Phase 2
│   ├── integration/         # Phase 3
│   ├── engine/              # Phase 4 — Groq
│   ├── presentation/        # DTO helpers / formatters for API
│   └── web/                 # Interim MVP (deprecate after 5b)
├── data/cache/              # Restaurant JSONL cache
├── Docs/
├── scripts/                 # Dev scripts (e.g. live tests)
└── tests/                   # Core tests; add backend/frontend tests in Phase 5
```

---

## Phase Dependencies (Build Order)

```mermaid
flowchart TD
    P0[Phase 0: Foundation]
    P1[Phase 1: Data]
    P2[Phase 2: Input]
    P3[Phase 3: Integration]
    P4[Phase 4: Groq Engine]
    P5A[Phase 5a: Backend API]
    P5B[Phase 5b: Frontend]
    P6[Phase 6: Hardening]
    P7[Phase 7: Railway + Vercel]

    P0 --> P1
    P0 --> P2
    P1 --> P3
    P2 --> P3
    P3 --> P4
    P4 --> P5A
    P2 --> P5A
    P5A --> P5B
    P5B --> P6
    P5B --> P7
    P6 --> P7
```

**Recommended order:** 0 → 1 → 2 → 3 → 4 → **5a → 5b** → (6) → **7 (deploy)**

Phases **5a** and **5b** can be developed in parallel once OpenAPI contract is agreed (contract-first).

---

## Traceability to Problem Statement

| Problem statement section | Architecture phase |
|---------------------------|-------------------|
| Data ingestion | Phase 1 |
| User input | Phase 2 + Phase 5b (form) |
| Integration layer | Phase 3 |
| Recommendation engine | Phase 4 (Groq) |
| Output display | Phase 5a (API) + Phase 5b (UI) |
| Deployment (production) | Phase 7 (Railway + Vercel) |

---

## MVP vs Full Build

| Scope | Phases | Stack |
|-------|--------|-------|
| **Current MVP** | 0–4 + interim web | Python `zm`, FastAPI + Jinja in `src/zm/web/` |
| **Target product** | 0–5b | `src/zm` core + `backend/` (FastAPI) + `frontend/` (Next.js) |
| **Production** | 0–7 | Next.js on Vercel + FastAPI on Railway (+ Phase 6 hardening) |
| **Local Docker** | 0–6 | `docker compose up` (API + web) |

---

## Migration Notes (interim web → proper B/F)

1. Extract orchestration from `src/zm/web/app.py` into `backend/services/recommendation_service.py` (call `zm.engine.recommend`).
2. Move HTTP routes to `backend/api/routes/` with versioned `/api/v1` prefix.
3. Build React app calling the same JSON shape already used by `POST /api/preferences`.
4. Keep `zm serve` as alias to backend only, or run `uvicorn backend.main:app` + `npm run dev` in frontend.
5. Remove Jinja templates once frontend reaches exit criteria.
6. Deploy Phase 7 per [Deployment-Railway-Vercel.md](./Deployment-Railway-Vercel.md).

This architecture keeps structured filtering and Groq in the Python core, with a clear boundary: **frontend (Vercel) = UX**, **backend (Railway) = HTTP + orchestration**, **zm = domain logic**.

---

## Related documentation

- [Deployment-Railway-Vercel.md](./Deployment-Railway-Vercel.md) — Railway + Vercel deployment plan
- [GoogleStitch-UI-Prompt.md](./GoogleStitch-UI-Prompt.md) — copy-paste prompt for Google Stitch to generate the **Next.js** frontend UI
- [EdgeCases.md](./EdgeCases.md)
