FROM python:3.11-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip hatchling

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
COPY backend ./backend

RUN python -m pip install --no-cache-dir -e .

ENV PYTHONPATH=/app
ENV WEB_HOST=0.0.0.0
ENV DATASET_CACHE_DIR=/app/data/cache
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips=*"]
