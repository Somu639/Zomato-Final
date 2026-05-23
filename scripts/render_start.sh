#!/usr/bin/env bash
# Optional Render entrypoint — prefer the uvicorn startCommand in render.yaml.
set -euo pipefail

export PYTHONUNBUFFERED=1
export WEB_HOST="${WEB_HOST:-0.0.0.0}"
export RENDER="${RENDER:-true}"
export PYTHONPATH="${PYTHONPATH:-.}:${RENDER_PROJECT_DIR:-.}"

cd "${RENDER_PROJECT_DIR:-$(pwd)}"

exec uvicorn backend.main:create_app \
  --factory \
  --host 0.0.0.0 \
  --port "${PORT:?PORT is not set}" \
  --proxy-headers \
  --forwarded-allow-ips='*'
