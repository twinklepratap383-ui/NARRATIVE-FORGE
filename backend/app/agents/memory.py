"""Memory Agent.

Implements the recency + importance weighting from the strategy doc's T3
resolution: recent memories score higher, and high-importance memories
(secrets revealed, emotional peaks) always surface regardless of age.
"""
from __future__ import annotations

from .base import Agent
from ..schemas import Character, Memory


class MemoryAgent(Agent):
    name = "memory"

    def retrieve(self, character: Character, current_turn: int, k: int = 4) -> list[Memory]:
        def score(m: Memory) -> float:
            recency = 1.0 / (1.0 + max(0, current_turn - m.turn))
            # High-importance memories get a large constant boost so they
            # surface even when old.
            return recency * 0.6 + m.importance * 0.4 + (1.0 if m.importance >= 0.8 else 0.0)

        ranked = sorted(character.memories, key=score, reverse=True)
        return ranked[:k]

    def summarise(self, character: Character, current_turn: int) -> str:
        mems = self.retrieve(character, current_turn)
        if not mems:
            return "(no notable memories yet)"
        return "\n".join(f"- (turn {m.turn}) {m.content}" for m in mems)
