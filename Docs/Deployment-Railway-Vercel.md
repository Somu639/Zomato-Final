# Deployment Plan: Railway (Backend) + Vercel (Frontend)

Production target for **ZM**: FastAPI on [Railway](https://railway.com), Next.js on [Vercel](https://vercel.com).

Repository: [Somu639/Zomato-Final](https://github.com/Somu639/Zomato-Final)

---

## Architecture

```mermaid
flowchart LR
    User[User browser]
    Vercel[Vercel — Next.js]
    Railway[Railway — FastAPI]
    Groq[Groq API]
    HF[Hugging Face dataset]

    User --> Vercel
    Vercel -->|HTTPS JSON| Railway
    Railway --> Groq
    Railway --> HF
```

| Component | Host | URL (example) |
|-----------|------|----------------|
| Frontend | Vercel | `https://zomato-final.vercel.app` |
| Backend API | Railway | `https://zm-api-production.up.railway.app` |
| Secrets | Railway env only | `GROQ_API_KEY` never in Vercel |

---

## Part 1 — Backend on Railway

### 1.1 What gets deployed

- Entry: `backend/main.py` → `uvicorn backend.main:create_app --factory`
- Config: [`railway.toml`](../railway.toml), [`Procfile`](../Procfile), [`nixpacks.toml`](../nixpacks.toml)
- Build: `pip install -e .` (from root `requirements.txt`)
- Data: loads from cache if present; otherwise downloads in a **background thread** after the server starts (deploy health check stays fast)

### 1.2 Create the service (Dashboard)

1. [Railway Dashboard](https://railway.com/new) → **Deploy from GitHub repo** → **Somu639/Zomato-Final**, branch `main`.
2. **Root directory**: leave empty (repository root — not `frontend/`).
3. Railway auto-detects Python via Nixpacks; config is overridden by `railway.toml` if present.

| Setting | Value |
|---------|--------|
| **Build Command** | `pip install -e .` |
| **Start Command** | `uvicorn backend.main:create_app --factory --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips='*'` |
| **Health Check** | `/health` |

4. **Variables** (Railway → service → Variables):

| Key | Required | Example / notes |
|-----|----------|-----------------|
| `GROQ_API_KEY` | Yes (for AI rankings) | From Groq console |
| `CORS_ORIGINS` | Yes | `https://your-app.vercel.app` (set after Vercel deploy) |
| `WEB_HOST` | Recommended | `0.0.0.0` |
| `DATASET_CACHE_DIR` | No | `data/cache` |
| `LOG_LEVEL` | No | `INFO` |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` |

Railway sets `PORT` and `RAILWAY_ENVIRONMENT` automatically.

5. **Generate domain**: Settings → Networking → **Generate Domain**.

### 1.3 Verify backend

```bash
curl https://YOUR-SERVICE.up.railway.app/health
curl https://YOUR-SERVICE.up.railway.app/api/v1/locations
```

Open `https://YOUR-SERVICE.up.railway.app/docs` for OpenAPI.

First deploy may return `"data_loaded": false` for 1–2 minutes while the dataset downloads in the background.

### 1.4 Railway notes

| Topic | Guidance |
|-------|----------|
| **Ephemeral disk** | Cache is rebuilt on redeploy unless you attach a [Railway Volume](https://docs.railway.com/guides/volumes) at `data/cache` |
| **Build failures** | Check logs; ensure root directory is repo root and `pip install -e .` succeeds |
| **PORT** | Railway injects `$PORT`; start command must bind to it |
| **Monorepo** | Do not set root to `frontend/` for the API service |

---

## Part 2 — Frontend on Vercel

### 2.1 Create the project

1. [Vercel Dashboard](https://vercel.com/new) → Import **Somu639/Zomato-Final**.
2. **Root Directory** → `frontend`.
3. **Environment variable**:

| Key | Value |
|-----|--------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://YOUR-SERVICE.up.railway.app` (no trailing slash, no `/api`) |

4. Deploy.

### 2.2 Local dev

Leave `NEXT_PUBLIC_API_BASE_URL` empty; `next.config.ts` proxies `/api` to `http://127.0.0.1:8000`.

---

## Part 3 — Wire CORS

After Vercel gives you a URL, set on Railway:

```env
CORS_ORIGINS=https://your-project.vercel.app
```

Redeploy or wait for Railway to restart the service.

---

## Part 4 — Checklist

### Backend (Railway)

- [ ] Service deployed from repo root on `main`
- [ ] Build: `pip install -e .` succeeds
- [ ] Public domain generated
- [ ] `GROQ_API_KEY` set
- [ ] `/health` returns 200
- [ ] `CORS_ORIGINS` includes Vercel URL

### Frontend (Vercel)

- [ ] Root directory = `frontend`
- [ ] `NEXT_PUBLIC_API_BASE_URL` = Railway HTTPS URL
- [ ] End-to-end: form → recommendations

---

## Part 5 — Environment matrix

| Variable | Railway | Vercel | Local |
|----------|---------|--------|-------|
| `GROQ_API_KEY` | ✅ | ❌ | `.env` |
| `CORS_ORIGINS` | ✅ | ❌ | `.env` |
| `NEXT_PUBLIC_API_BASE_URL` | ❌ | ✅ | `frontend/.env.local` |
| `DATASET_CACHE_DIR` | ✅ | ❌ | `data/cache` |
| `PORT` | ✅ (auto) | ❌ | `WEB_PORT` |

---

## Part 6 — Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Deploy failed / health timeout | Build blocked on dataset download | Use latest `main` (background prefetch); build is `pip install -e .` only |
| `{"detail":"Not Found"}` on `/api/v1/*` | Wrong start command or legacy `zm serve` | Use uvicorn start command above |
| `NEXT_PUBLIC_API_BASE_URL` ends with `/api` | Double path → 404 | Use Railway domain only |
| CORS error | Missing Vercel URL in `CORS_ORIGINS` | Update Railway variables |
| `data_loaded: false` | Cache still downloading | Wait 1–2 min; check Railway logs |
| Groq fallback only | Missing `GROQ_API_KEY` on Railway | Set variable in Railway |

---

## Related docs

- [PhaseWiseArchitecture.md](./PhaseWiseArchitecture.md)
- [README.md](../README.md)
- [frontend/.env.example](../frontend/.env.example)
