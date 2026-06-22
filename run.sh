#!/usr/bin/env bash
# One command to run the whole app (API + frontend on one port).
set -e

# Install dependencies (quiet; skips quickly if already installed).
pip install -q -r requirements.txt

# Create .env from the template on first run so the app starts cleanly.
if [ ! -f .env ]; then
  cp .env.example .env
  echo "──────────────────────────────────────────────────────────"
  echo "  Created .env — open it and paste your GEMINI_API_KEY."
  echo "  (AI extraction stays off until you do; manual entry works.)"
  echo "──────────────────────────────────────────────────────────"
fi

echo "Starting MTA NOL Tracker on http://localhost:8000"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
