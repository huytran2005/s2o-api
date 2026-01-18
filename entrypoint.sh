#!/bin/sh
set -e

echo "Starting S2O API container..."

# -----------------------------
# 1. Validate required env vars
# -----------------------------
REQUIRED_VARS="DATABASE_URL RABBITMQ_URL JWT_SECRET_KEY MEDIA_ROOT"

for var in $REQUIRED_VARS; do
  if [ -z "$(eval echo \$$var)" ]; then
    echo "ERROR: Environment variable $var is not set"
    exit 1
  fi
done

# -----------------------------
# 2. Wait for database
# -----------------------------
echo "Waiting for database to be ready..."

until python - <<EOF
from sqlalchemy import create_engine, text
import os, sys

engine = create_engine(os.environ["DATABASE_URL"])
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    print(e)
    sys.exit(1)
EOF
do
  echo "Database not ready, retrying in 2s..."
  sleep 2
done

echo "Database is ready."

# -----------------------------
# 3. Run migrations
# -----------------------------
echo "Running Alembic migrations..."
alembic upgrade head
echo "Migrations completed."

# -----------------------------
# 4. Start application
# -----------------------------
echo "Starting FastAPI..."
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000
