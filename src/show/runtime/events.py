"""Contrats typés des événements ``emit`` (runner / bridge UI)."""

from __future__ import annotations

from typing import Literal, TypedDict, Union


class TurnEvent(TypedDict):
    type: Literal["turn"]
    agent: str
    name: str
    round: int
    text: str
    tactic: str
    evidence_used: bool


class ModeratorEvent(TypedDict):
    type: Literal["moderator"]
    round: int
    text: str


class InnerMonologueEvent(TypedDict):
    type: Literal["inner_monologue"]
    agent: str
    text: str


class StanceUpdateEvent(TypedDict):
    type: Literal["stance_update"]
    round: int
    tension: float
    stances: dict[str, float]
    convictions: dict[str, float]


class StepEvent(TypedDict):
    type: Literal["step"]
    agent: str
    name: str
    label: str
    round: int


class EarpieceEvent(TypedDict):
    type: Literal["earpiece"]
    phase: Literal["opening", "live"]
    text: str


ShowEvent = Union[
    TurnEvent,
    ModeratorEvent,
    InnerMonologueEvent,
    StanceUpdateEvent,
    StepEvent,
    EarpieceEvent,
]

EMIT_EVENT_TYPES = frozenset(
    {"turn", "moderator", "inner_monologue", "stance_update", "step", "earpiece"}
)


def validate_emit_event(event: dict) -> None:
    """Lève ``ValueError`` si l'événement n'a pas de ``type`` connu."""
    kind = event.get("type")
    if kind not in EMIT_EVENT_TYPES:
        raise ValueError(f"unknown emit event type: {kind!r}")
