"""NarrativeForge FastAPI application entrypoint.

Run locally:  uvicorn app.main:app --reload
OpenAPI docs: http://localhost:8000/docs
"""
from __future__ import annotations

import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import get_settings
from .routes import meta, stories

settings = get_settings()

app = FastAPI(
    title="NarrativeForge",
    description="Interactive Cinematic Story Engine — a multi-agent narrative "
                "intelligence system.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(stories.router)

# Serve the no-build demo frontend at / if present.
_FRONTEND = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "index.html"


@app.get("/", include_in_schema=False, response_model=None)
async def root() -> FileResponse | dict:
    if _FRONTEND.exists():
        return FileResponse(str(_FRONTEND))
    return {"app": "NarrativeForge", "docs": "/docs"}
