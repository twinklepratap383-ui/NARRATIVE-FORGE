"""Narrator Agent.

Stateless. Renders cinematic connective prose around the spoken line so the
scene reads like a film, not a chat log. Uses GPT-4o (the expensive model) per
the cost strategy — narration is the only player-facing prose.
"""
from __future__ import annotations

from .base import Agent
from ..schemas import AgentTrace, WorldState


_NARRATOR_SYS = """You are the Narrator of a cinematic Victorian mystery.
Write ONE short, atmospheric sentence of stage-setting prose (no dialogue) that
frames the moment. Match the tension level: higher tension, tauter prose.
Setting: {setting}. Tension: {tension:.2f}."""


class NarratorAgent(Agent):
    name = "narrator"

    async def narrate(self, world: WorldState, beat: str) -> tuple[str, list[AgentTrace]]:
        system = _NARRATOR_SYS.format(setting=world.setting, tension=world.tension)
        prose = (await self.llm.complete(system, f"The moment: {beat}", temperature=0.9)).strip()
        return prose, [self.trace("render", "Rendered cinematic transition prose.")]
