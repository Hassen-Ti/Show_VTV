"""Contexte runtime du show (injecté via ``context=`` à l'invoke LangGraph)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from openai import OpenAI

from show.runtime.events import ShowEvent

# Événements typés : voir ``show.runtime.events.ShowEvent``.
EmitCallback = Callable[[ShowEvent | dict[str, Any]], None]

# Sonde régie → oreillette : renvoie la consigne en attente (et la consomme), ou None.
EarpiecePoll = Callable[[], Optional[str]]
EarpiecePeek = Callable[[], bool]


@dataclass
class ShowContext:
    """Dépendances runtime — non persistées dans l'état."""

    client: Optional[OpenAI] = None
    model_internal: str = ""
    model_delivery: str = ""
    enable_web_search: bool = True
    emit: Optional[EmitCallback] = None
    poll_earpiece: Optional[EarpiecePoll] = None
    peek_earpiece: Optional[EarpiecePeek] = None
    trace_llm_cursor: Optional[Callable[[], int]] = None
    rng: Callable[[], float] = field(default=random.random)


def emit_event(context: ShowContext, event: dict[str, Any]) -> None:
    if context.emit:
        context.emit(event)  # type: ignore[arg-type]


def drain_earpiece(context: ShowContext) -> str:
    """Consigne du producteur en attente dans l'oreillette du modérateur ('' sinon)."""
    if context.poll_earpiece is None:
        return ""
    return (context.poll_earpiece() or "").strip()


def has_earpiece(context: ShowContext) -> bool:
    """True si un message spectateur attend d'être lu par le modérateur.

    Source unique pour le routage post-``update_shared_state`` (via
    ``decide_after_update``). Ne pas re-câbler un ``peek`` parallèle sur le graphe.
    """
    if context.peek_earpiece is not None:
        return context.peek_earpiece()
    return False
