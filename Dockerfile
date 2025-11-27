FROM python:3.12-slim

WORKDIR /app

# Install system deps for pip and graceful shutdown
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install runtime dependencies
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Use PORT env var (Cloud Run uses 8080 by default)
ENV PORT 8080

# Expose the port
EXPOSE 8080

# Use gunicorn with a single worker for the legacy Flask UI (kept in `legacy/`)
# Note: ADK deployments do not require this Dockerfile. This container image
# preserves the legacy Flask server for local testing.
CMD ["gunicorn", "-w", "1", "-k", "gthread", "-b", "0.0.0.0:8080", "legacy.server_flask:app"]
