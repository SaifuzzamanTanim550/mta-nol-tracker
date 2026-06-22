"""Configuration — loads environment variables.

The API key is read from the environment, never hardcoded.
Locally it comes from the .env file; in production from the host's
environment variables.
"""
import os
from dotenv import load_dotenv

# Load variables from .env (if present) into the environment.
load_dotenv()

# Kept for reference; no longer the active provider.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# ── OpenAI (active AI provider) ──────────────────────────────────────
# Do NOT paste your key in this file.
# Local / Codespace:  .env   →   OPENAI_API_KEY=sk-your_key_here
# Production (Render): add it under the host's Environment Variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
# ─────────────────────────────────────────────────────────────────────

# Where persistent data lives.
DATA_DIR = os.environ.get("DATA_DIR", "data")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")

# Comma-separated list of allowed CORS origins ("*" allows all).
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")