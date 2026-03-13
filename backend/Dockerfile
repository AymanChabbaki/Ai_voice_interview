# Multi-stage build
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.prod.txt .

# Install PyTorch CPU + all requirements
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      torch==2.2.0 torchvision==0.17.0 && \
    pip install --no-cache-dir -r requirements.prod.txt && \
    # Safe cleanup only - remove .pyc files and pip cache
    find /usr/local/lib/python3.11/site-packages -type f -name '*.pyc' -delete && \
    find /usr/local/lib/python3.11/site-packages -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true && \
    # Remove torch C++ headers (not needed at runtime) - saves ~200MB
    rm -rf /usr/local/lib/python3.11/site-packages/torch/include && \
    # Remove caffe2 (not needed for inference)
    rm -rf /usr/local/lib/python3.11/site-packages/caffe2 && \
    # Clean pip/tmp cache
    rm -rf /root/.cache /tmp/* /var/tmp/*

# Final stage - minimal runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY . .

# Create cache directory and clean up dev artifacts
RUN mkdir -p /app/.cache && chmod 777 /app/.cache && \
    rm -rf /app/__pycache__ /app/.git /app/.pytest_cache /app/htmlcov /app/tests

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=1 \
    LOG_LEVEL=info

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]