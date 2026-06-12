"""Foundry IQ grounding.

Addresses weakness W2 from the strategy doc ("the Foundry IQ integration is
thin"). This module does two things:

1. Semantic grounding: retrieves narrative-theory passages relevant to the
   current dramatic situation, so character reasoning is grounded in craft
   rather than vibes.
2. Procedural memory: records which narrative tactics produced strong player
   engagement, so across sessions the Director can prefer what worked.

When a real Foundry project is configured it calls the knowledge base; offline
it uses a small bundled corpus. Either way the contract is identical.
"""
from __future__ import annotations

from typing import Any

from .config import get_settings

# A compact bundled corpus standing in for the Foundry IQ knowledge base.
_NARRATIVE_KB: list[dict[str, str]] = [
    {
        "tags": "confrontation pressure suspect alibi",
        "text": ("Under pressure, well-drawn suspects deflect rather than flatly "
                 "contradict. They introduce a detail that is technically true but "
                 "misleading, preserving deniability while buying time."),
    },
    {
        "tags": "secret tension reveal partial truth",
        "text": ("Partial truth sustains tension: reveal just enough to be believed "
                 "while concealing the core secret. Total denial reads as guilt; full "
                 "disclosure ends the drama."),
    },
    {
        "tags": "pacing act tension escalation",
        "text": ("Escalate tension in waves, not a straight line. A brief release "
                 "after a peak makes the next peak land harder. Hold the act open until "
                 "a genuine reversal earns the turn."),
    },
    {
        "tags": "character goal motivation loyalty",
        "text": ("A character's secret goal should colour every line without ever "
                 "being stated. Loyalty under threat produces protective evasion, not "
                 "aggression."),
    },
    {
        "tags": "victorian period detail setting drawing room",
        "text": ("Victorian drawing-room scenes favour restraint and propriety. "
                 "Emotion is signalled through small physical tells — a tightened glove, "
                 "a too-careful pause — rather than open display."),
    },
]


class FoundryIQ:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Any = None
        self._procedural: list[str] = []
        if self.settings.foundry_configured:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            self._client = AIProjectClient(
                endpoint=self.settings.foundry_project_endpoint,
                credential=DefaultAzureCredential(),
            )

    @property
    def live(self) -> bool:
        return self._client is not None

    async def ground(self, situation: str, genre: str, top_k: int = 2) -> str:
        """Return narrative-theory context for the current situation."""
        if self._client is not None:
            resp = await self._client.knowledge_bases.query(  # pragma: no cover
                knowledge_base_id=self.settings.foundry_kb_id,
                query=f"Genre: {genre}. Situation: {situation}. What narrative principles apply?",
                top_k=top_k,
            )
            return "\n".join(d.content for d in resp.documents)

        # Offline: rank the bundled corpus by keyword overlap.
        words = set(re.findall(r"[a-z]+", (situation + " " + genre).lower()))
        scored = sorted(
            _NARRATIVE_KB,
            key=lambda d: len(words & set(d["tags"].split())),
            reverse=True,
        )
        return "\n".join(d["text"] for d in scored[:top_k])

    def record_tactic(self, tactic: str, engagement: float) -> None:
        """Procedural memory: remember tactics that engaged the player."""
        if engagement >= 0.6:
            self._procedural.append(tactic)

    def recall_tactics(self) -> list[str]:
        return self._procedural[-5:]


import re  # noqa: E402  (kept at bottom to keep the module body readable)

_foundry: FoundryIQ | None = None


def get_foundry() -> FoundryIQ:
    global _foundry
    if _foundry is None:
        _foundry = FoundryIQ()
    return _foundry
