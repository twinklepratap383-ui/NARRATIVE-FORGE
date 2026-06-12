"""Agent base class. Every agent shares an LLM handle and emits reasoning
traces so the Reasoning Panel can show judges *why* each decision was made.
"""
from __future__ import annotations

from ..llm import LLM, get_llm
from ..schemas import AgentTrace


class Agent:
    name: str = "agent"

    def __init__(self, llm: LLM | None = None) -> None:
        self.llm = llm or get_llm()

    def trace(self, step: str, detail: str) -> AgentTrace:
        return AgentTrace(agent=self.name, step=step, detail=detail)
