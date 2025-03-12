# syntax=docker/dockerfile:1

# Base image with shared configurations
FROM python:3.11-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/app/src

WORKDIR /app

# Install global dependencies
RUN pip install uv uvicorn

# Development image
FROM python-base as development
ENV FASTAPI_ENV=development

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install dependencies
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install -e . && \
    uv pip install pytest pytest-cov black isort

# Development command
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source /app/.venv/bin/activate && exec uvicorn address_matcher.main:app --host 0.0.0.0 --port 8000 --reload"]

# Production image
FROM python-base as production
ENV FASTAPI_ENV=production

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install dependencies
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install -e .

# Production command with workers
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source /app/.venv/bin/activate && exec uvicorn address_matcher.main:app --host 0.0.0.0 --port 8000 --workers 4"] 