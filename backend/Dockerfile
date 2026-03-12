# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install only essential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.prod.txt .

# Install PyTorch CPU wheels first, then production requirements only, then aggressively clean
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      torch==2.2.0 torchvision==0.17.0 && \
    pip install --no-cache-dir -r requirements.prod.txt && \
    find /usr/local/lib/python3.11/site-packages -type f -name '*.pyc' -delete && \
    find /usr/local/lib/python3.11/site-packages -type d -name '__pycache__' -delete && \
    find /usr/local/lib/python3.11/site-packages -type d -name '*.dist-info' -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf /root/.cache /tmp/* /var/tmp/* /build

# Final stage - minimal runtime image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only runtime dependencies (postgres client if needed for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder - only site-packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY . .

# Create directory for models cache
RUN mkdir -p /app/.cache && chmod 777 /app/.cache && \
    rm -rf /app/__pycache__ /app/.git /app/.pytest_cache /app/htmlcov /app/tests

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=1 \
    LOG_LEVEL=info

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application

# Run the application
CMD ["python", "app.py"]
