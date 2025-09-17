# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --no-dev

# Copy application code
COPY *.py ./
COPY pdf_parser.py database_manager.py api_server.py ./

# Create directory for database and cache, and fix permissions for OpenShift
RUN mkdir -p /app/data /tmp/.cache && \
    chmod -R 777 /app/data /tmp/.cache && \
    # Fix permissions for the virtual environment
    chmod -R 755 /app/.venv && \
    # Make sure all binaries in .venv/bin are executable
    find /app/.venv/bin -type f -exec chmod a+x {} \; && \
    # Support arbitrary user IDs (OpenShift requirement)
    chgrp -R 0 /app && \
    chmod -R g=u /app && \
    # Ensure .venv/bin/python is specifically executable
    chmod 755 /app/.venv/bin/python*

# Run as non-root user (OpenShift will assign one)
USER 1001

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/submissions.db
ENV UV_CACHE_DIR=/tmp/.cache/uv
ENV UV_NO_CACHE=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application using shell to handle PATH properly
CMD ["sh", "-c", "cd /app && .venv/bin/python -m uvicorn api_server:app --host 0.0.0.0 --port 8000"]
