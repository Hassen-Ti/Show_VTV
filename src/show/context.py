"""Contexte runtime du show (injecté via ``context=`` à l'invoke LangGraph)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from openai import OpenAI

# Événement émis vers le runner : {"type": "turn"|"moderator"|"inner_monologue"|
# "stance_update"|"step", ...}
EmitCallback = Callable[[dict[str, Any]], None]


@dataclass
class ShowContext:
    """Dépendances runtime — non persistées dans l'état."""

    client: Optional[OpenAI] = None
    model_internal: str = ""
    model_delivery: str = ""
    enable_web_search: bool = True
    emit: Optional[EmitCallback] = None
    rng: Callable[[], float] = field(default=random.random)


def emit_event(context: ShowContext, event: dict[str, Any]) -> None:
    if context.emit:
        context.emit(event)
