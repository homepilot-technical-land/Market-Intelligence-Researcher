# Multi-stage production Dockerfile for HomePilot Market Intelligence Engine
# Based on Python 3.12-slim with non-root security isolation

# --- Stage 1: Build & Wheels ---
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Runtime Image ---
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime utilities (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged application user
RUN groupadd -g 1001 homepilot && \
    useradd -u 1001 -g homepilot -m -s /bin/bash homepilot

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/homepilot/.local
ENV PATH=/home/homepilot/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY --chown=homepilot:homepilot . .

# Switch to non-root user
USER homepilot

# Healthcheck probe against RFC 7807 FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Default command launches FastAPI via Uvicorn
CMD ["uvicorn", "src.api.intelligence_api:app", "--host", "0.0.0.0", "--port", "8000"]
