# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    python3-dev \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

WORKDIR /app

COPY . .

RUN useradd --no-create-home --shell /bin/false appuser && \
    chown -R appuser:appuser /app

RUN mkdir -p /app/staticfiles /app/mediafiles && \
    chown -R appuser:appuser /app/staticfiles /app/mediafiles

USER appuser

ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings.prod_settings
# appuser has no home dir (--no-create-home); point HOME at a writable path
# so gunicorn's control-socket state doesn't fail with permission denied.
ENV HOME=/app

# Dummy values so collectstatic can import settings at build time without real secrets/DB.
RUN SECRET_KEY=dummy-build-key DATABASE_URL=postgresql://user:pass@localhost:5432/dummy \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", \
     "--workers", "3", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "config.wsgi:application"]
