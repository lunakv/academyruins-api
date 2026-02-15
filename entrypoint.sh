#!/bin/sh
set -e

echo "Waiting for database..."
while ! python -c "
from src.db import engine
engine.connect().close()
" 2>/dev/null; do
    sleep 2
done
echo "Database is ready"

echo "Running migrations..."
poetry run alembic upgrade head

echo "Running bootstrap (skips if already seeded)..."
poetry run academyruins bootstrap

echo "Starting API server..."
exec poetry run uvicorn src.main:app --proxy-headers --forwarded-allow-ips=* --host 0.0.0.0 --port 80
