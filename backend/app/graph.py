"""LangGraph orchestration (optional showcase).

The :class:`Orchestrator` is the runtime engine. This module exposes the *same*
pipeline as an explicit LangGraph ``StateGraph`` for the architecture diagram
and for judges who want to see the graph topology. It imports LangGraph lazily
so the core engine runs even if LangGraph is not installed.

    character -> consequence -> director -> narrator -> END

Run ``build_graph()`` to get a compiled graph; its node functions delegate to
the shared agent instances, so there is a single source of truth for logic.
"""
from __future__ import annotations

from typing import Any, TypedDict

from .orchestrator import get_orchestrator


class TurnState(TypedDict, total=False):
    story: Any
    speak_to: str
    message: str
    line: str
    traces: list
    deltas: dict


def build_graph():  # pragma: no cover - exercised only when langgraph installed
    from langgraph.graph import END, StateGraph

    orch = get_orchestrator()

    async def character_node(state: TurnState) -> TurnState:
        story = state["story"]
        char = story.characters[state["speak_to"]]
        from .scenarios import SCENARIOS
        genre = SCENARIOS[story.scenario_id]["genre"]
        line, traces = await orch.character.respond(
            char, state["message"], story.world, genre, story.turn
        )
        state["line"] = line
        state["traces"] = list(traces)
        return state

    async def consequence_node(state: TurnState) -> TurnState:
        story = state["story"]
        char = story.characters[state["speak_to"]]
        traces, deltas = await orch.consequence.process(
            story.world, char, state["message"], state["line"], story.turn
        )
        orch.character.update_emotions(char, deltas)
        state["traces"] += traces
        return state

    async def director_node(state: TurnState) -> TurnState:
        story = state["story"]
        traces = await orch.director.direct(
            story.world, state["message"], state["line"], story.turn
        )
        state["traces"] += traces
        return state

    async def narrator_node(state: TurnState) -> TurnState:
        story = state["story"]
        char = story.characters[state["speak_to"]]
        prose, traces = await orch.narrator.narrate(
            story.world, f"{char.name} has answered."
        )
        state["traces"] += traces
        return state

    g = StateGraph(TurnState)
    g.add_node("character", character_node)
    g.add_node("consequence", consequence_node)
    g.add_node("director", director_node)
    g.add_node("narrator", narrator_node)
    g.set_entry_point("character")
    g.add_edge("character", "consequence")
    g.add_edge("consequence", "director")
    g.add_edge("director", "narrator")
    g.add_edge("narrator", END)
    return g.compile()
