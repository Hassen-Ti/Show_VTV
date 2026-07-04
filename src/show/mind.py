"""Algorithmes de conscience agentique — fonctions pures, testables sans LLM.

Le score de persuasion est produit par un juge LLM dans le nœud ``listen`` puis
injecté ici ; ces fonctions ne font que la dynamique (dérive, émotions, tension).
"""

from __future__ import annotations

from config.show_config import (
    AROUSAL_DECAY,
    CONCEDE_THRESHOLD,
    DRIFT_LR,
    TENSION_AROUSAL_WEIGHT,
    TENSION_ATTACK_WEIGHT,
    VALENCE_RECOVERY,
)
from show.personas.vector import AGGRESSIVE_TACTICS, PersonaVector
from show.state import MindState, TranscriptEntry


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def revise_stance(
    mind: MindState,
    persona: PersonaVector,
    opponent_stance: float,
    persuasion: float,
) -> MindState:
    """Dérive d'opinion : un bon argument adverse rapproche la stance de l'adversaire.

    delta = persuasion * openness * DRIFT_LR, où openness dépend de la
    stubbornness (trait) et de la conviction courante (état).
    """
    gap = opponent_stance - mind["stance"]
    openness = (1.0 - persona.stubbornness) * (1.0 - mind["conviction"])
    delta = persuasion * openness * DRIFT_LR
    step = min(delta, abs(gap))
    direction = 1.0 if gap > 0 else -1.0 if gap < 0 else 0.0
    new = dict(mind)
    new["stance"] = _clamp(mind["stance"] + direction * step, -1.0, 1.0)
    return new  # type: ignore[return-value]


def update_conviction(mind: MindState, persuasion: float, countered: bool) -> MindState:
    """Contrer renforce la conviction ; être ébranlé sans répondre l'érode."""
    delta = 0.05 if countered else -0.05 * persuasion
    new = dict(mind)
    new["conviction"] = _clamp(mind["conviction"] + delta, 0.1, 1.0)
    return new  # type: ignore[return-value]


def should_concede(persuasion: float, persona: PersonaVector, rand: float) -> bool:
    """Concession structurelle : argument trop fort, ou trait de caractère."""
    return persuasion > CONCEDE_THRESHOLD or rand < persona.concession_rate


def appraise(mind: MindState, persona: PersonaVector, event: str) -> MindState:
    """Appraisal émotionnel (valence / arousal) selon l'événement du tour.

    Événements : attacked_personal | attacked_moral | conceded_to_me | argument.
    """
    valence = mind["valence"]
    arousal = mind["arousal"]
    if event in ("attacked_personal", "attacked_moral"):
        arousal += persona.arousal_gain * 0.3
        valence -= 0.2
    elif event == "conceded_to_me":
        valence += 0.3
        arousal -= 0.1
    elif event == "argument":
        arousal += persona.arousal_gain * 0.1
    new = dict(mind)
    new["valence"] = _clamp(valence, -1.0, 1.0)
    new["arousal"] = _clamp(arousal, 0.0, 1.0)
    return new  # type: ignore[return-value]


def decay(mind: MindState, persona: PersonaVector) -> MindState:
    """Fin de round : l'excitation retombe, l'humeur revient vers la baseline."""
    new = dict(mind)
    new["arousal"] = _clamp(mind["arousal"] * AROUSAL_DECAY, 0.0, 1.0)
    new["valence"] = _clamp(
        mind["valence"] + (persona.affective_baseline - mind["valence"]) * VALENCE_RECOVERY,
        -1.0,
        1.0,
    )
    return new  # type: ignore[return-value]


def effective_voice_temperature(mind: MindState, persona: PersonaVector) -> float:
    """Plus l'agent est à chaud, plus sa voix est débridée."""
    return persona.temperature_voice + 0.4 * mind["arousal"]


def effective_sentence_max(mind: MindState, persona: PersonaVector, high_arousal: float) -> int:
    """À chaud, les répliques deviennent plus sèches."""
    if mind["arousal"] > high_arousal:
        return max(1, persona.sentence_max - 1)
    return persona.sentence_max


def compute_tension(
    minds: dict[str, MindState],
    last_round_entries: list[TranscriptEntry],
) -> float:
    """Température du plateau : émotions des invités + densité d'attaques."""
    arousals = [m["arousal"] for m in minds.values()]
    mean_arousal = sum(arousals) / len(arousals) if arousals else 0.0
    guest_entries = [e for e in last_round_entries if e["role"] == "guest"]
    if guest_entries:
        attacks = sum(1 for e in guest_entries if e["tactic"] in AGGRESSIVE_TACTICS)
        attack_density = attacks / len(guest_entries)
    else:
        attack_density = 0.0
    return _clamp(
        TENSION_AROUSAL_WEIGHT * mean_arousal + TENSION_ATTACK_WEIGHT * attack_density,
        0.0,
        1.0,
    )
