"""Configuration — loads environment variables.

The Gemini API key is read from the environment, never hardcoded.
Locally it comes from the .env file; in production from the host's
environment variables.
"""
import os
from dotenv import load_dotenv

# Load variables from .env (if present) into the environment.
load_dotenv()

# ── SET YOUR GEMINI API KEY ──────────────────────────────────────────
# Do NOT paste your key in this file.
# Local / Codespace:  put it in  .env   →   GEMINI_API_KEY=your_key_here
# Production (Render/Vercel): add it under the host's Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# ─────────────────────────────────────────────────────────────────────

# Model is configurable so you can swap it without touching code.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Where persistent data lives.
DATA_DIR = os.environ.get("DATA_DIR", "data")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")

# Comma-separated list of allowed CORS origins ("*" allows all).
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
