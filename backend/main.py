"""MTA NOL Tracker — application entry point.

Serves the JSON API under /api and the static frontend at /, so the whole
app runs from one server on one port. In Codespace: `./run.sh`.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config
from .routers import extract, records, memo

app = FastAPI(title="MTA NOL Tracker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes first…
app.include_router(extract.router)
app.include_router(records.router)
app.include_router(memo.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini_key_set": bool(config.GEMINI_API_KEY)}


# …then the frontend mounted at root (html=True serves index.html).
_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/", StaticFiles(directory=_FRONTEND_DIR, html=True), name="frontend")
