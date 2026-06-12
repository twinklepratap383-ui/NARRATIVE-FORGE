"""Core data models for NarrativeForge.

These pydantic models are the shared "blackboard" that every agent reads from
and writes to. Keeping them in one place keeps the agent contracts honest.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id() -> str:
    return uuid4().hex[:12]


class Emotion(str, Enum):
    FEAR = "fear"
    TRUST = "trust"
    ANGER = "anger"
    LOVE = "love"
    LOYALTY = "loyalty"
    CONFIDENCE = "confidence"


class RelationType(str, Enum):
    TRUST = "trust"
    HATRED = "hatred"
    FRIENDSHIP = "friendship"
    ALLIANCE = "alliance"
    ROMANCE = "romance"
    RIVALRY = "rivalry"


class Memory(BaseModel):
    """A single episodic memory held by a character."""

    id: str = Field(default_factory=_id)
    turn: int
    content: str
    importance: float = 0.5  # 0..1 — high-importance memories always surface
    emotional_impact: float = 0.0  # -1..1
    created_at: datetime = Field(default_factory=_now)


class EmotionState(BaseModel):
    """Each emotion sits in 0..1. Updated by the Emotion logic each turn."""

    fear: float = 0.1
    trust: float = 0.5
    anger: float = 0.1
    love: float = 0.1
    loyalty: float = 0.5
    confidence: float = 0.6

    def clamp(self) -> "EmotionState":
        for f in self.model_fields:
            setattr(self, f, max(0.0, min(1.0, getattr(self, f))))
        return self

    @property
    def stress(self) -> float:
        """A single 0..1 stress signal the Director and Character agents use."""
        return min(1.0, (self.fear * 0.5 + self.anger * 0.3 + (1 - self.confidence) * 0.4))


class Character(BaseModel):
    id: str
    name: str
    role: str
    personality: str
    public_goal: str
    secret_goal: str
    emotions: EmotionState = Field(default_factory=EmotionState)
    memories: list[Memory] = Field(default_factory=list)
    knows: list[str] = Field(default_factory=list)  # facts this character knows

    def add_memory(self, turn: int, content: str, importance: float = 0.5,
                   emotional_impact: float = 0.0) -> None:
        self.memories.append(
            Memory(turn=turn, content=content, importance=importance,
                   emotional_impact=emotional_impact)
        )


class Relationship(BaseModel):
    source: str  # character id
    target: str  # character id
    type: RelationType
    weight: float = 0.5  # 0..1 strength of the relationship


class Clue(BaseModel):
    id: str = Field(default_factory=_id)
    text: str
    revealed_turn: int


class WorldState(BaseModel):
    """The persistent ground truth the Consequence Agent maintains."""

    setting: str = ""
    facts: dict[str, str] = Field(default_factory=dict)
    clues: list[Clue] = Field(default_factory=list)
    tension: float = 0.2  # 0..1, owned by the Director Agent
    act: int = 1
    truth: str = ""  # the hidden solution (never sent to the player)


class AgentTrace(BaseModel):
    """A single reasoning step, surfaced to judges in the Reasoning Panel."""

    agent: str
    step: str
    detail: str


class Scene(BaseModel):
    id: str = Field(default_factory=_id)
    turn: int
    speaker: str  # character id or "narrator"
    text: str
    traces: list[AgentTrace] = Field(default_factory=list)
    tension: float = 0.2
    created_at: datetime = Field(default_factory=_now)


class Story(BaseModel):
    id: str = Field(default_factory=_id)
    title: str
    scenario_id: str
    world: WorldState
    characters: dict[str, Character]
    relationships: list[Relationship] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)
    turn: int = 0
    solved: bool = False
    created_at: datetime = Field(default_factory=_now)


# ---- API request/response models -------------------------------------------

class CreateStoryRequest(BaseModel):
    scenario_id: str = "victorian_murder"
    title: Optional[str] = None


class PlayerAction(BaseModel):
    """A turn of play. Either address a character or make an accusation."""

    speak_to: Optional[str] = None  # character id
    message: Optional[str] = None
    accuse: Optional[str] = None  # character id being accused


class TurnResult(BaseModel):
    story_id: str
    turn: int
    scenes: list[Scene]
    tension: float
    act: int
    solved: bool
    clues: list[Clue]
