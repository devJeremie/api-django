# Dev image — runs manage.py runserver, not a production WSGI/ASGI server.
# slim base keeps the image small; the apt packages below are only needed to
# compile mysqlclient (a C extension) at pip-install time.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependances systeme necessaires pour compiler mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt copied and installed before the rest of the source so
# Docker's layer cache is reused across builds as long as dependencies
# haven't changed (source edits alone don't invalidate this layer).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0, not 127.0.0.1 — the dev server must accept connections from
# outside the container (i.e. from the host, via docker-compose's port
# mapping), not just from localhost inside the container.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
