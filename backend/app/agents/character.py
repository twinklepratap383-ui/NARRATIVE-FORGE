"""Character Agent.

The heart of the system. For the addressed character it:
  1. retrieves relevant memory (Memory Agent),
  2. grounds the situation in narrative theory (Foundry IQ),
  3. reasons in-character toward its *secret* goal,
  4. updates its emotional state.

Output is a spoken line plus the reasoning trace shown to judges.
"""
from __future__ import annotations

from .base import Agent
from .memory import MemoryAgent
from ..foundry import FoundryIQ, get_foundry
from ..schemas import AgentTrace, Character, EmotionState, WorldState


_SYSTEM = """You are {name}, {role}.
Personality: {personality}
Your SECRET goal (never state it openly): {secret_goal}
Your public stance: {public_goal}
Current stress: {stress:.2f} (0 calm .. 1 cornered)

NARRATIVE CRAFT (from Foundry IQ — apply it, do not quote it):
{grounding}

WHAT YOU KNOW:
{knowledge}

WHAT YOU REMEMBER:
{memory}

Rules:
- Stay perfectly in character and in period.
- Never reveal your secret goal directly. Under pressure, deflect with a
  technically-true but misleading detail rather than flatly contradicting.
- Respond with 2-4 sentences of dialogue, with a brief physical tell if stressed.
- Do NOT break character or mention being an AI."""


class CharacterAgent(Agent):
    name = "character"

    def __init__(self, llm=None, foundry: FoundryIQ | None = None) -> None:
        super().__init__(llm)
        self.foundry = foundry or get_foundry()
        self.memory = MemoryAgent(self.llm)

    async def respond(
        self,
        character: Character,
        player_message: str,
        world: WorldState,
        genre: str,
        turn: int,
    ) -> tuple[str, list[AgentTrace]]:
        traces: list[AgentTrace] = []

        mem_summary = self.memory.summarise(character, turn)
        traces.append(self.trace("memory_retrieval",
                                  f"Surfaced {len(self.memory.retrieve(character, turn))} "
                                  f"relevant memories for {character.name}."))

        situation = f"{character.name} is questioned: '{player_message}'"
        grounding = await self.foundry.ground(situation, genre)
        traces.append(self.trace("foundry_iq",
                                  "Grounded in narrative craft: " + grounding.split('.')[0] + "."))

        stress = character.emotions.stress
        traces.append(self.trace("conflict_analysis",
                                  f"Stress {stress:.2f}. Secret goal at "
                                  f"{'high' if stress > 0.6 else 'moderate'} risk; choosing "
                                  f"{'deflection' if stress > 0.5 else 'measured candour'}."))

        system = _SYSTEM.format(
            name=character.name,
            role=character.role,
            personality=character.personality,
            secret_goal=character.secret_goal,
            public_goal=character.public_goal,
            stress=stress,
            grounding=grounding,
            knowledge="\n".join(f"- {k}" for k in character.knows),
            memory=mem_summary,
        )
        user = f"The investigator says to you: \"{player_message}\"\nRespond in character."
        line = (await self.llm.complete(system, user, temperature=0.85)).strip()

        traces.append(self.trace("decision", "Delivered in-character response consistent "
                                              "with memory and secret goal."))

        # Record the exchange in this character's memory.
        character.add_memory(
            turn,
            f"I was asked: '{player_message}'. I replied guardedly.",
            importance=0.5 + 0.3 * stress,
            emotional_impact=-0.3 * stress,
        )
        return line, traces

    def update_emotions(self, character: Character, deltas: dict[str, float]) -> EmotionState:
        e = character.emotions
        for field, delta in deltas.items():
            if hasattr(e, field):
                setattr(e, field, getattr(e, field) + float(delta))
        return e.clamp()
