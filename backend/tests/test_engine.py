"""Engine-level tests. These run fully offline against the mock LLM."""
from __future__ import annotations

import pytest

from app.orchestrator import Orchestrator
from app.scenarios import build_story
from app.schemas import PlayerAction


@pytest.fixture
def story():
    return build_story("victorian_murder")


@pytest.fixture
def orch():
    return Orchestrator()


@pytest.mark.asyncio
async def test_opening_scene(orch, story):
    scene = await orch.opening(story)
    assert scene.speaker == "narrator"
    assert scene.text
    assert len(story.scenes) == 1


@pytest.mark.asyncio
async def test_dialogue_turn_produces_narration_and_dialogue(orch, story):
    await orch.opening(story)
    result = await orch.play_turn(
        story,
        PlayerAction(speak_to="ashworth", message="Where were you that evening?"),
    )
    assert result.turn == 1
    speakers = {s.speaker for s in result.scenes}
    assert "narrator" in speakers
    assert "ashworth" in speakers
    # Reasoning traces are present for the demo Reasoning Panel.
    dialogue = next(s for s in result.scenes if s.speaker == "ashworth")
    steps = {t.step for t in dialogue.traces}
    assert "memory_retrieval" in steps
    assert "foundry_iq" in steps
    assert "decision" in steps


@pytest.mark.asyncio
async def test_memory_accumulates_across_turns(orch, story):
    await orch.opening(story)
    char = story.characters["ashworth"]
    before = len(char.memories)
    for _ in range(3):
        await orch.play_turn(
            story, PlayerAction(speak_to="ashworth", message="Tell me about the library.")
        )
    assert len(char.memories) > before


@pytest.mark.asyncio
async def test_cross_character_awareness(orch, story):
    await orch.opening(story)
    await orch.play_turn(
        story, PlayerAction(speak_to="ashworth", message="Where were you?")
    )
    # The butler should now have a memory that Ashworth was questioned.
    butler = story.characters["hargrove"]
    assert any("questioned" in m.content for m in butler.memories)


@pytest.mark.asyncio
async def test_correct_accusation_solves_story(orch, story):
    await orch.opening(story)
    result = await orch.play_turn(story, PlayerAction(accuse="crane"))
    assert result.solved is True
    assert story.world.act == 3


@pytest.mark.asyncio
async def test_wrong_accusation_keeps_mystery(orch, story):
    await orch.opening(story)
    result = await orch.play_turn(story, PlayerAction(accuse="ashworth"))
    assert result.solved is False


@pytest.mark.asyncio
async def test_invalid_action_raises(orch, story):
    await orch.opening(story)
    with pytest.raises(ValueError):
        await orch.play_turn(story, PlayerAction())


@pytest.mark.asyncio
async def test_tension_stays_bounded(orch, story):
    await orch.opening(story)
    for _ in range(6):
        await orch.play_turn(
            story, PlayerAction(speak_to="crane", message="Why were you really here?")
        )
    assert 0.0 <= story.world.tension <= 1.0
