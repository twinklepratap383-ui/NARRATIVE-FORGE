"""Orchestrator.

Executes one player turn through the agent pipeline in the dependency-safe
order from the strategy doc (T2):

    player input -> Character -> Consequence -> Director -> Narrator -> output

The addressed character runs synchronously; other character agents only update
their awareness asynchronously (latency mitigation T1). State lives on the
``Story`` object so the whole thing is serialisable and resumable.
"""
from __future__ import annotations

from .agents import CharacterAgent, ConsequenceAgent, DirectorAgent, NarratorAgent
from .scenarios import SCENARIOS
from .schemas import (
    AgentTrace,
    PlayerAction,
    Scene,
    Story,
    TurnResult,
)


class Orchestrator:
    def __init__(self) -> None:
        self.character = CharacterAgent()
        self.consequence = ConsequenceAgent()
        self.director = DirectorAgent()
        self.narrator = NarratorAgent()

    async def opening(self, story: Story) -> Scene:
        """Render the opening narration when a story is created."""
        beat = (
            f"The investigation begins. {story.world.facts.get('victim', '')} "
            f"{story.world.facts.get('cause', '')}"
        )
        prose, traces = await self.narrator.narrate(story.world, beat)
        scene = Scene(turn=0, speaker="narrator", text=prose, traces=traces,
                      tension=story.world.tension)
        story.scenes.append(scene)
        return scene

    async def play_turn(self, story: Story, action: PlayerAction) -> TurnResult:
        story.turn += 1
        turn = story.turn
        new_scenes: list[Scene] = []

        if action.accuse:
            new_scenes.extend(await self._handle_accusation(story, action.accuse, turn))
        elif action.speak_to and action.message:
            new_scenes.extend(await self._handle_dialogue(story, action, turn))
        else:
            raise ValueError("Action must include either (speak_to + message) or accuse.")

        story.scenes.extend(new_scenes)
        return TurnResult(
            story_id=story.id,
            turn=turn,
            scenes=new_scenes,
            tension=story.world.tension,
            act=story.world.act,
            solved=story.solved,
            clues=story.world.clues,
        )

    # -- pipeline branches --------------------------------------------------

    async def _handle_dialogue(self, story: Story, action: PlayerAction,
                               turn: int) -> list[Scene]:
        char = story.characters.get(action.speak_to or "")
        if char is None:
            raise KeyError(f"No character '{action.speak_to}' in this story.")
        genre = SCENARIOS[story.scenario_id]["genre"]

        # 1. Character speaks (grounded, in-character).
        line, char_traces = await self.character.respond(
            char, action.message or "", story.world, genre, turn
        )

        # 2. Consequence: world + emotion updates.
        cons_traces, deltas = await self.consequence.process(
            story.world, char, action.message or "", line, turn
        )
        self.character.update_emotions(char, deltas)

        # 3. Director: pacing + tension.
        dir_traces = await self.director.direct(
            story.world, action.message or "", line, turn
        )

        # 4. Cross-character awareness: other characters note the exchange (async-style,
        #    cheap memory write only — no extra LLM calls).
        for other_id, other in story.characters.items():
            if other_id != char.id:
                other.add_memory(turn, f"{char.name} was questioned by the investigator.",
                                 importance=0.3)

        traces: list[AgentTrace] = char_traces + cons_traces + dir_traces

        # 5. Narrator frames the beat.
        prose, narr_traces = await self.narrator.narrate(
            story.world, f"{char.name} has just answered under questioning."
        )

        narration = Scene(turn=turn, speaker="narrator", text=prose,
                          traces=narr_traces, tension=story.world.tension)
        dialogue = Scene(turn=turn, speaker=char.id, text=line, traces=traces,
                         tension=story.world.tension)
        return [narration, dialogue]

    async def _handle_accusation(self, story: Story, accused_id: str,
                                 turn: int) -> list[Scene]:
        accused = story.characters.get(accused_id)
        if accused is None:
            raise KeyError(f"No character '{accused_id}' to accuse.")
        correct, resolution = self.consequence.evaluate_accusation(story.world, accused)
        story.solved = correct
        if correct:
            story.world.tension = 1.0
            story.world.act = 3

        trace = AgentTrace(
            agent="consequence",
            step="accusation_evaluated",
            detail=f"Accusation of {accused.name} evaluated against world truth: "
                   f"{'CORRECT' if correct else 'incorrect'}.",
        )
        return [Scene(turn=turn, speaker="narrator", text=resolution,
                      traces=[trace], tension=story.world.tension)]


_orchestrator: Orchestrator | None = None


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
