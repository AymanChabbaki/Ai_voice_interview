# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 – Builder
#   Installs Python dependencies into an isolated prefix.
#   Uses the full image so compilers are available for psycopg2-binary / torch.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

WORKDIR /install

# System build deps (needed only at build time – discarded in final stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Use CPU-only PyTorch wheel (~250 MB vs ~2 GB for CUDA) – no GPU in Docker/K8s
RUN pip install --no-cache-dir --prefix=/install/pkg \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 – Runtime
#   Copies only the installed packages and application code.
#   No build tools → smaller, leaner image.
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.10-slim AS runtime

# Runtime system deps (libpq for psycopg2 at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install/pkg /usr/local

WORKDIR /app

# Copy application source
COPY app.py      .
COPY database.py .
COPY final_knowledge_base.csv .
COPY course_catalog.csv .

# Model artefacts are mounted from a Kubernetes volume at /app/models.
# CSV datasets are mounted at /app/data.
# Nothing else is baked into the image to keep it as small as possible.

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser \
    # Pre-create the HF cache dir as appuser so the Docker volume mount
    # inherits the right ownership (volume root would be owned by root otherwise)
    && mkdir -p /app/.cache/huggingface \
    && chown -R appuser:appuser /app

USER appuser

# Expose backend port
EXPOSE 8000

# Sentence-transformers caches models here; mount as emptyDir or PVC in K8s
ENV HF_HOME=/app/.cache/huggingface
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Uvicorn is driven entirely by environment variables (PORT, WORKERS, RELOAD, LOG_LEVEL)
CMD ["sh", "-c", "uvicorn app:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --log-level ${LOG_LEVEL:-info}"]
