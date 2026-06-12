"""Director Agent.

Owns pacing. After the consequences are known it adjusts the tension meter and
decides whether to advance the act. It records which tactics engaged the player
into Foundry IQ procedural memory (strategy doc Upgrade 3).
"""
from __future__ import annotations

from .base import Agent
from ..foundry import FoundryIQ, get_foundry
from ..schemas import AgentTrace, WorldState


_DIRECTOR_SYS = """You are the Story Director for an interactive mystery.
Manage pacing in waves, not a straight line. Given the current tension and the
latest exchange, reply with JSON only:
{"tension_delta": <float -0.2..0.3>, "advance_act": <bool>, "note": <string>}"""


class DirectorAgent(Agent):
    name = "director"

    def __init__(self, llm=None, foundry: FoundryIQ | None = None) -> None:
        super().__init__(llm)
        self.foundry = foundry or get_foundry()

    async def direct(
        self,
        world: WorldState,
        player_message: str,
        spoken_line: str,
        turn: int,
    ) -> list[AgentTrace]:
        traces: list[AgentTrace] = []

        prior = self.foundry.recall_tactics()
        if prior:
            traces.append(self.trace("procedural_memory",
                                     f"Recalling {len(prior)} tactics that engaged players "
                                     "in prior sessions."))

        payload = (
            f"Current tension: {world.tension:.2f}. Act: {world.act}. Turn: {turn}.\n"
            f"Investigator: {player_message}\n"
            f"Response: {spoken_line}\n"
            f"Clues so far: {len(world.clues)}."
        )
        result = await self.llm.complete_json(_DIRECTOR_SYS, payload, cheap=True)

        delta = float(result.get("tension_delta", 0.05))
        world.tension = max(0.0, min(1.0, world.tension + delta))

        advanced = False
        if result.get("advance_act") and world.tension > 0.6 and world.act < 3:
            world.act += 1
            advanced = True

        note = result.get("note", "Tension adjusted.")
        traces.append(self.trace("pacing",
                                  f"Tension {world.tension:.2f} (Δ{delta:+.2f}). "
                                  f"{'Advanced to act ' + str(world.act) + '. ' if advanced else ''}{note}"))

        # Record the probing tactic as engaging if it raised tension.
        if delta > 0.1:
            self.foundry.record_tactic(f"direct probe about '{player_message[:40]}'", 0.7)
        return traces
