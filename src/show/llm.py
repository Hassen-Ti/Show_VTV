"""Façade LLM du show — point de mock unique pour les tests.

Délègue aux utilitaires existants du pipeline débatteur (non modifiés).
"""

from __future__ import annotations

from typing import Optional

from openai import OpenAI

from agents.react.nodes.common import invoke_internal
from agents.react.tools.search import execute_search_web


def think(
    model: str,
    system: str,
    user: str,
    *,
    temperature: float,
    max_tokens: Optional[int] = None,
) -> str:
    """Appel LLM interne (raisonnement, jamais diffusé tel quel)."""
    return invoke_internal(model, system, user, temperature=temperature, max_tokens=max_tokens)


def search(client: OpenAI, model: str, query: str) -> str:
    """Recherche web synthétisée pour un débat."""
    return execute_search_web(client, model, query)
