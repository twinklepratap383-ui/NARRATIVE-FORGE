"""Bundled scenarios.

The Victorian murder mystery is the theatrical demo closer from the strategy
doc. It ships with a hidden ground truth (``world.truth``) that the player must
deduce. Characters carry secret goals that colour every response.

A scenario is just data: add a dict to ``SCENARIOS`` to ship a new one (this is
the "open scenario framework" from Upgrade 5 in the strategy doc).
"""
from __future__ import annotations

from ..schemas import (
    Character,
    Clue,
    EmotionState,
    Relationship,
    RelationType,
    Story,
    WorldState,
)


def _victorian_murder() -> Story:
    ashworth = Character(
        id="ashworth",
        name="Lady Eleanor Ashworth",
        role="The widow of the house",
        personality="Composed, fiercely strategic, protective of family above all.",
        public_goal="Appear cooperative and grief-stricken; see the matter closed quickly.",
        secret_goal="Protect her son Julian from scandal at absolutely any cost.",
        emotions=EmotionState(trust=0.4, confidence=0.75, fear=0.2, loyalty=0.9),
        knows=[
            "I told everyone I was in the library all evening.",
            "I was actually in the garden for a quarter hour.",
            "My son Julian quarrelled bitterly with my late husband last week.",
        ],
    )
    hargrove = Character(
        id="hargrove",
        name="Mr. Hargrove",
        role="The family butler",
        personality="Discreet, loyal to the house, observant to a fault.",
        public_goal="Maintain the dignity of the household and answer plainly.",
        secret_goal="Shield Lady Ashworth, whom he has served for thirty years.",
        emotions=EmotionState(trust=0.5, confidence=0.7, loyalty=0.85),
        knows=[
            "The library was empty when I passed it at half nine.",
            "I saw a gown's hem damp with garden dew that night.",
            "I will not volunteer what I saw unless pressed directly.",
        ],
    )
    crane = Character(
        id="crane",
        name="Mr. Sebastian Crane",
        role="The late lord's business partner",
        personality="Smooth, ambitious, quick to redirect suspicion.",
        public_goal="Distance himself from the death and protect the firm's name.",
        secret_goal="Hide that he was being cut out of the business that very week.",
        emotions=EmotionState(trust=0.35, confidence=0.8, anger=0.25),
        knows=[
            "Lord Ashworth intended to dissolve our partnership.",
            "I was at the station catching the late train — or so I will say.",
            "I owe a great deal of money I cannot easily repay.",
        ],
    )

    world = WorldState(
        setting="Ashworth Manor, a fog-bound English estate, the winter of 1887.",
        facts={
            "victim": "Lord Reginald Ashworth, found dead in his study at half past ten.",
            "cause": "A blow to the head; the study window was found open.",
        },
        clues=[
            Clue(text="Lord Ashworth was found in his locked study with the window ajar.",
                 revealed_turn=0),
        ],
        tension=0.2,
        act=1,
        # The hidden solution. Never sent to the player; the Consequence Agent
        # checks accusations against it.
        truth=(
            "Sebastian Crane killed Lord Ashworth to stop being cut out of the firm. "
            "He entered through the garden window. Lady Ashworth saw him from the "
            "garden but has stayed silent because she feared her son Julian — who had "
            "also quarrelled with the victim — would be blamed."
        ),
    )

    relationships = [
        Relationship(source="ashworth", target="hargrove", type=RelationType.TRUST, weight=0.9),
        Relationship(source="hargrove", target="ashworth", type=RelationType.ALLIANCE, weight=0.9),
        Relationship(source="ashworth", target="crane", type=RelationType.RIVALRY, weight=0.6),
        Relationship(source="crane", target="ashworth", type=RelationType.RIVALRY, weight=0.7),
    ]

    return Story(
        title="The Ashworth Affair",
        scenario_id="victorian_murder",
        world=world,
        characters={c.id: c for c in (ashworth, hargrove, crane)},
        relationships=relationships,
    )


SCENARIOS: dict[str, dict] = {
    "victorian_murder": {
        "name": "The Ashworth Affair",
        "genre": "Victorian murder mystery",
        "blurb": "A locked study, a fog-bound estate, and three people with secrets.",
        "builder": _victorian_murder,
    },
}


def build_story(scenario_id: str, title: str | None = None) -> Story:
    if scenario_id not in SCENARIOS:
        raise KeyError(f"Unknown scenario: {scenario_id}")
    story = SCENARIOS[scenario_id]["builder"]()
    if title:
        story.title = title
    return story
