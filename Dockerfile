# Use a slim Python image for a smaller footprint on AWS
FROM python:3.13-slim-bookworm

# Install uv directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation and set environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies first (better caching)
COPY pyproject.toml .
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Sync the project itself
RUN uv sync --frozen --no-dev && \
    chmod +x migrate.sh

# Start the application using Gunicorn with Uvicorn workers for production stability
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--workers", "2", "--bind", "0.0.0.0:8000", "app.main:app"]