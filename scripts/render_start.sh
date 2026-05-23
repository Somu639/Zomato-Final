#!/usr/bin/env bash
# Render web service entrypoint (Phase 7). Run from repository root.
set -euo pipefail

export PYTHONUNBUFFERED=1
export WEB_HOST="${WEB_HOST:-0.0.0.0}"
export RENDER="${RENDER:-true}"

ROOT="${RENDER_PROJECT_DIR:-$(pwd)}"
cd "$ROOT"

if [[ ! -f backend/main.py ]]; then
  echo "ERROR: backend/main.py not found in $ROOT" >&2
  echo "Set Render Root Directory to empty (repository root), not frontend/." >&2
  exit 1
fi

python -c "import backend.main" 2>/dev/null || {
  echo "ERROR: cannot import backend.main — run: pip install -e ." >&2
  exit 1
}

PORT="${PORT:?PORT is not set (Render should inject this)}"

echo "Starting ZM API on 0.0.0.0:${PORT} (cwd=${ROOT})"
exec uvicorn backend.main:create_app \
  --factory \
  --host 0.0.0.0 \
  --port "$PORT" \
  --proxy-headers \
  --forwarded-allow-ips='*'
