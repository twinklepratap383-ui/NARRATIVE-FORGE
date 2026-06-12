"""Analytics and health endpoints.

Analytics powers the frontend tension chart, relationship graph and emotion
panels — all derived from the live Story state.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..llm import get_llm
from ..foundry import get_foundry
from ..store import get_store

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health")
async def health() -> dict:
    s = get_settings()
    return {
        "status": "ok",
        "app": s.app_name,
        "environment": s.environment,
        "azure_openai": "live" if get_llm().live else "mock",
        "foundry_iq": "live" if get_foundry().live else "offline-kb",
    }


@router.get("/stories/{story_id}/analytics")
async def analytics(story_id: str) -> dict:
    story = await get_store().get(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    tension_series = [{"turn": s.turn, "tension": s.tension} for s in story.scenes]
    relationships = [r.model_dump() for r in story.relationships]
    emotions = {
        cid: c.emotions.model_dump() | {"stress": round(c.emotions.stress, 3)}
        for cid, c in story.characters.items()
    }
    memory_counts = {cid: len(c.memories) for cid, c in story.characters.items()}
    return {
        "story_id": story.id,
        "turn": story.turn,
        "act": story.world.act,
        "tension_series": tension_series,
        "relationships": relationships,
        "emotions": emotions,
        "memory_counts": memory_counts,
        "clues": [c.model_dump() for c in story.world.clues],
        "solved": story.solved,
    }
