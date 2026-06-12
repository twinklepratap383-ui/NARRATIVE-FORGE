"""Runtime configuration. Everything is env-driven so the same image runs
locally (offline mock LLM) and on Azure (real Azure OpenAI) with no code change.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NarrativeForge"
    environment: str = "local"

    # Azure OpenAI. If endpoint+key+deployment are all set, the real client is
    # used. Otherwise the engine falls back to the deterministic mock LLM so the
    # demo runs with zero cloud setup.
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_deployment_mini: str = "gpt-4o-mini"
    azure_openai_api_version: str = "2024-10-21"

    # Azure AI Foundry (Foundry IQ knowledge base) — optional grounding.
    foundry_project_endpoint: str = ""
    foundry_kb_id: str = ""

    # Infra
    redis_url: str = ""  # empty -> in-memory store
    cors_origins: str = "*"

    @property
    def azure_configured(self) -> bool:
        return bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and self.azure_openai_deployment
        )

    @property
    def foundry_configured(self) -> bool:
        return bool(self.foundry_project_endpoint and self.foundry_kb_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()
