"""Story endpoints: create a story, fetch it, play a turn, list scenarios."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..orchestrator import get_orchestrator
from ..scenarios import SCENARIOS, build_story
from ..schemas import (
    CreateStoryRequest,
    PlayerAction,
    Story,
    TurnResult,
)
from ..store import get_store

router = APIRouter(prefix="/api", tags=["stories"])


@router.get("/scenarios")
async def list_scenarios() -> list[dict]:
    return [
        {"id": sid, "name": s["name"], "genre": s["genre"], "blurb": s["blurb"]}
        for sid, s in SCENARIOS.items()
    ]


@router.post("/stories", response_model=Story)
async def create_story(req: CreateStoryRequest) -> Story:
    try:
        story = build_story(req.scenario_id, req.title)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await get_orchestrator().opening(story)
    await get_store().save(story)
    return story


@router.get("/stories/{story_id}", response_model=Story)
async def get_story(story_id: str) -> Story:
    story = await get_store().get(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.post("/stories/{story_id}/turn", response_model=TurnResult)
async def play_turn(story_id: str, action: PlayerAction) -> TurnResult:
    store = get_store()
    story = await store.get(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    if story.solved:
        raise HTTPException(status_code=409, detail="This story is already solved.")
    try:
        result = await get_orchestrator().play_turn(story, action)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await store.save(story)
    return result
