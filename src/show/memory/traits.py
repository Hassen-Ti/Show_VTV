"""Traits minimaux pour la dynamique mind — sans dépendance vers guests.

``PersonaVector`` satisfait structurellement ``MindTraits`` (duck typing).
``AGGRESSIVE_TACTICS`` vit ici : constante de physique du plateau (tension),
pas d'identité invité. Les guests réexportent pour compat.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

# Tactiques considérées comme agressives (alimentent la tension du plateau).
AGGRESSIVE_TACTICS = frozenset(
    {"clash", "moral_attack", "expose_hypocrisy", "contradiction"}
)


@runtime_checkable
class MindTraits(Protocol):
    """Sous-ensemble de traits lus par ``memory.mind`` / ``initial_mind``."""

    agent_id: str
    stubbornness: float
    concession_rate: float
    arousal_gain: float
    affective_baseline: float
    temperature_voice: float
    sentence_max: int
    initial_stance: float
    initial_conviction: float
