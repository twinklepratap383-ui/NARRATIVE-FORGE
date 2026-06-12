"""Consequence Agent.

Owns the world's ground truth. After a character speaks it:
  - extracts any new clue the exchange surfaced,
  - records consequences as world facts,
  - computes emotion deltas for the addressed character,
  - and, for accusations, evaluates them against the hidden truth.
"""
from __future__ import annotations

from .base import Agent
from ..schemas import AgentTrace, Character, Clue, WorldState


_CONSEQUENCE_SYS = """You are the Consequence Agent for an interactive mystery.
Given the exchange, decide what changed in the world. Reply with JSON only:
{"new_facts": {<key>: <value>}, "clue": <string or null>, "world_note": <string>}
A clue is a concrete, player-visible detail that advances the investigation.
Do not reveal the solution."""

_EMOTION_SYS = """You are the Emotion Agent. Given a character and an exchange,
output emotion DELTAS in [-0.3, 0.3] as JSON with keys:
fear, anger, trust, confidence, loyalty, love. Negative values lower the emotion."""


class ConsequenceAgent(Agent):
    name = "consequence"

    async def process(
        self,
        world: WorldState,
        speaker: Character,
        player_message: str,
        spoken_line: str,
        turn: int,
    ) -> tuple[list[AgentTrace], dict[str, float]]:
        traces: list[AgentTrace] = []

        payload = (
            f"Exchange with {speaker.name}.\n"
            f"Investigator: {player_message}\n"
            f"{speaker.name}: {spoken_line}\n"
            f"Known facts: {world.facts}"
        )
        result = await self.llm.complete_json(_CONSEQUENCE_SYS, payload, cheap=True)

        for k, v in (result.get("new_facts") or {}).items():
            world.facts[str(k)] = str(v)

        clue_text = result.get("clue")
        if clue_text:
            world.clues.append(Clue(text=str(clue_text), revealed_turn=turn))
            traces.append(self.trace("clue_registered",
                                      f"New clue surfaced: {clue_text}"))
        else:
            traces.append(self.trace("world_update",
                                      result.get("world_note", "World state noted the exchange.")))

        emotion = await self.llm.complete_json(_EMOTION_SYS, payload, cheap=True)
        deltas = {k: float(v) for k, v in emotion.items()
                  if k in ("fear", "anger", "trust", "confidence", "loyalty", "love")}
        traces.append(self.trace("emotion_update",
                                  f"Adjusted {speaker.name}'s emotional state ({len(deltas)} signals)."))
        return traces, deltas

    def evaluate_accusation(self, world: WorldState, accused: Character) -> tuple[bool, str]:
        """True solution names Sebastian Crane. Encodes the hidden truth check."""
        correct = accused.id == "crane"
        if correct:
            return True, (
                "The room falls silent. Crane's composure finally cracks — the alibi "
                "of the late train was a lie, the garden window his way in. The truth "
                "of the Ashworth affair is laid bare."
            )
        return False, (
            f"{accused.name} regards the accusation coldly. \"You are mistaken, and "
            "your mistake is dangerous.\" The real culprit watches, unbothered. The "
            "mystery holds."
        )
