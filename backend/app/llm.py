"""LLM access layer.

One async ``complete()`` call serves the whole engine. If Azure OpenAI is
configured it routes there (GPT-4o for narration, GPT-4o-mini for cheaper
internal reasoning, per the cost strategy). If not, a deterministic mock
generates plausible in-character text so the full demo runs offline.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional

from .config import get_settings


class LLM:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Any = None
        if self.settings.azure_configured:
            # Imported lazily so the package installs/run even without the SDK.
            from openai import AsyncAzureOpenAI

            self._client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_key=self.settings.azure_openai_api_key,
                api_version=self.settings.azure_openai_api_version,
            )

    @property
    def live(self) -> bool:
        return self._client is not None

    async def complete(
        self,
        system: str,
        user: str,
        *,
        cheap: bool = False,
        temperature: float = 0.8,
        json_mode: bool = False,
    ) -> str:
        if self._client is None:
            return _mock_complete(system, user, json_mode=json_mode)

        deployment = (
            self.settings.azure_openai_deployment_mini
            if cheap
            else self.settings.azure_openai_deployment
        )
        kwargs: dict[str, Any] = {
            "model": deployment,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = await self._client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    async def complete_json(self, system: str, user: str, *, cheap: bool = True) -> dict:
        raw = await self.complete(system, user, cheap=cheap, json_mode=True, temperature=0.4)
        return _safe_json(raw)


# --------------------------------------------------------------------------- #
#  Deterministic offline mock — keeps the demo fully playable without Azure.
# --------------------------------------------------------------------------- #

def _safe_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
    return {}


def _mock_complete(system: str, user: str, *, json_mode: bool) -> str:
    """A cheap but coherent stand-in. It reads role hints out of the system
    prompt so different agents produce visibly different output."""
    s = system.lower()

    if json_mode:
        # Used by Consequence / Director / Emotion reasoning steps.
        if "consequence" in s:
            return json.dumps({
                "new_facts": {},
                "clue": _mock_clue(user),
                "world_note": "The player pressed on a sensitive thread.",
            })
        if "director" in s:
            return json.dumps({
                "tension_delta": 0.12,
                "advance_act": False,
                "note": "Pressure is building; hold the act and tighten the screws.",
            })
        if "emotion" in s:
            return json.dumps({
                "fear": 0.1, "anger": 0.05, "trust": -0.05,
                "confidence": -0.08, "loyalty": 0.0, "love": 0.0,
            })
        return "{}"

    if "narrator" in s:
        return (
            "The gaslight gutters in its sconce. A hush settles over the drawing "
            "room as the question hangs in the air, heavy as the velvet drapes."
        )

    # Character agent. Pull the character name and stress out of the prompt.
    name = _grab(system, r"you are ([a-z .'-]+?),")
    stress = _grab(user, r"stress[: ]+([0-9.]+)") or _grab(system, r"stress[: ]+([0-9.]+)")
    name = (name or "the figure").title()
    try:
        stress_f = float(stress) if stress else 0.4
    except ValueError:
        stress_f = 0.4

    if stress_f > 0.6:
        return (
            f"{name} draws a slow breath. \"I have already told you where I was. "
            "I will not be made to repeat myself like a common suspect.\" The hands, "
            "though — the hands betray a tremor she cannot quite still."
        )
    return (
        f"{name} meets your gaze evenly. \"You may ask what you like. I have "
        "nothing to hide — though I confess the evening grows tiresome.\""
    )


def _mock_clue(user: str) -> Optional[str]:
    if any(w in user.lower() for w in ("library", "garden", "letter", "where")):
        return "A faint smear of garden soil was noted on the hem of a gown."
    return None


def _grab(text: str, pattern: str) -> Optional[str]:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


_llm: Optional[LLM] = None


def get_llm() -> LLM:
    global _llm
    if _llm is None:
        _llm = LLM()
    return _llm
