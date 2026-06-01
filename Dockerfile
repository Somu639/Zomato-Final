FROM python:3.11-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip hatchling

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
COPY streamlit_app ./streamlit_app
COPY .streamlit ./.streamlit

RUN python -m pip install --no-cache-dir -e .

ENV PYTHONPATH=/app
ENV DATASET_CACHE_DIR=/app/data/cache
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["sh", "-c", "streamlit run streamlit_app/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true"]
