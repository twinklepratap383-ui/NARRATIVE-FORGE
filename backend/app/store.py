"""Story persistence.

In-memory by default (perfect for a demo and for tests). If ``REDIS_URL`` is
set, stories are mirrored to Redis so multiple backend replicas share state on
Azure Container Apps. The async interface is identical either way.
"""
from __future__ import annotations

from typing import Optional

from .config import get_settings
from .schemas import Story


class StoryStore:
    def __init__(self) -> None:
        self._mem: dict[str, Story] = {}
        self._redis = None
        url = get_settings().redis_url
        if url:
            import redis.asyncio as redis  # lazy import

            self._redis = redis.from_url(url, decode_responses=True)

    async def save(self, story: Story) -> None:
        self._mem[story.id] = story
        if self._redis is not None:
            await self._redis.set(f"story:{story.id}", story.model_dump_json())

    async def get(self, story_id: str) -> Optional[Story]:
        if story_id in self._mem:
            return self._mem[story_id]
        if self._redis is not None:
            raw = await self._redis.get(f"story:{story_id}")
            if raw:
                story = Story.model_validate_json(raw)
                self._mem[story_id] = story
                return story
        return None

    async def list_ids(self) -> list[str]:
        return list(self._mem.keys())


_store: Optional[StoryStore] = None


def get_store() -> StoryStore:
    global _store
    if _store is None:
        _store = StoryStore()
    return _store
