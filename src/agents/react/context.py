"""Contexte d'exécution LangGraph (injecté via ``context=`` à l'invoke)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from openai import OpenAI

StepCallback = Callable[[str], None]
SearchCallback = Callable[[str], None]


@dataclass
class DebateGraphContext:
    """Dépendances runtime — non persistées par le checkpointer LangGraph."""

    client: OpenAI
    search_model: str
    step_callback: Optional[StepCallback] = None
    search_callback: Optional[SearchCallback] = None
