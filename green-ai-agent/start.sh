#!/bin/bash

# Startup script for Green AI Email Classification Agent

set -euo pipefail

echo "Starting Green AI Email Classification Agent..."

# Check if this is first run
if [ ! -f "/app/models/.initialized" ]; then
    echo "First run detected - downloading models..."
    python - <<'PY'
from transformers import pipeline
from backend.config import LIGHT_MODEL, HEAVY_MODEL

print('Downloading light model...')
pipeline('text-classification', model=LIGHT_MODEL, device=-1)

print('Downloading heavy model...')
pipeline('text-classification', model=HEAVY_MODEL, device=-1)

print('Models ready!')
PY

    touch /app/models/.initialized
fi

# Initialize database
echo "Initializing database..."
python - <<'PY'
from backend.main import init_email_db
init_email_db()
print('Database ready!')
PY

# Start the application
echo "Starting application..."

if [ "${1:-backend}" = "backend" ]; then
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
elif [ "$1" = "dashboard" ]; then
    exec streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0
else
    # Default: start backend
    exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
fi

