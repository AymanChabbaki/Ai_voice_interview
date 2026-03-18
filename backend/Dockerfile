FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# ✅ Add backend/ prefix
COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      torch==2.2.0 torchvision==0.17.0 && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.11/site-packages -type f -name '*.pyc' -delete && \
    rm -rf /usr/local/lib/python3.11/site-packages/torch/include && \
    rm -rf /usr/local/lib/python3.11/site-packages/caffe2 && \
    rm -rf /root/.cache /tmp/* /var/tmp/*

FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages \
                    /usr/local/lib/python3.11/site-packages

# ✅ Copy backend code with prefix
COPY backend/ .

# ✅ Copy CSV files from project root
COPY final_knowledge_base.csv /app/final_knowledge_base.csv
COPY course_catalog.csv /app/course_catalog.csv

RUN mkdir -p /app/.cache && chmod 777 /app/.cache && \
    rm -rf /app/__pycache__ /app/.git /app/.pytest_cache \
           /app/htmlcov /app/tests

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=1 \
    LOG_LEVEL=info \
    KB_FILE=/app/final_knowledge_base.csv \
    COURSES_FILE=/app/course_catalog.csv

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "app.py"]
