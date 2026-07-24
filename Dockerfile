FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
COPY knowledge_base ./knowledge_base
COPY scripts ./scripts
# The default PyPI torch wheel pulls CUDA libraries. This CPU-only web app does not need them.
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0+cpu \
    && pip install . \
    && useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

USER appuser
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
