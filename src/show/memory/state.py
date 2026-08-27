"""État partagé du show : le monde commun que tous les agents lisent/écrivent.

Contrat :
- les invités lisent ``transcript`` et n'écrivent que ``minds[leur_id]``, ``turn``
  et une entrée de transcript ;
- le modérateur lit ``tension`` / ``stance_history`` et écrit ``current_speaker``,
  ``moderator_notes`` et le transcript ;
- ``update_shared_state`` (moteur) recalcule ``tension`` et historise les stances.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from show.guests.personas.vector import PersonaVector


class TranscriptEntry(TypedDict):
    round: int
    speaker: str        # agent_id (clé stable)
    speaker_name: str   # nom affichable
    role: str           # guest | moderator
    text: str
    tactic: str
    evidence_used: bool


class MindState(TypedDict):
    stance: float          # opinion courante [-1, 1]
    conviction: float      # certitude [0, 1]
    valence: float         # humeur [-1, 1]
    arousal: float         # excitation [0, 1]
    beliefs: list[str]     # faits acceptés (mémoire)
    grudges: list[str]     # attaques subies non répondues
    inner_monologue: str   # pensée privée du dernier tour


class ShowState(TypedDict, total=False):
    topic: str
    round: int
    max_rounds: int
    turn_index: int
    transcript: Annotated[list[TranscriptEntry], operator.add]
    current_speaker: str
    minds: dict[str, MindState]
    tension: float
    stance_history: dict[str, list[float]]
    moderator_notes: Annotated[list[str], operator.add]
    turn: dict[str, Any]  # scratch du tour courant (claim, angle, evidence, tactic…)
    # Question spectateur drainée en interjection ; consommée par le prochain listen.
    pending_audience_question: str


def initial_mind(persona: PersonaVector) -> MindState:
    return MindState(
        stance=persona.initial_stance,
        conviction=persona.initial_conviction,
        valence=persona.affective_baseline,
        arousal=0.2,
        beliefs=[],
        grudges=[],
        inner_monologue="",
    )


def initial_show_state(
    topic: str,
    guests: list[PersonaVector],
    max_rounds: int,
) -> ShowState:
    return ShowState(
        topic=topic,
        round=0,
        max_rounds=max_rounds,
        turn_index=0,
        transcript=[],
        current_speaker="",
        minds={g.agent_id: initial_mind(g) for g in guests},
        tension=0.0,
        stance_history={g.agent_id: [g.initial_stance] for g in guests},
        moderator_notes=[],
        turn={},
        pending_audience_question="",
    )


def last_guest_entry(state: ShowState, *, exclude: str) -> TranscriptEntry | None:
    """Dernière réplique d'invité qui n'est pas ``exclude`` (la voix adverse)."""
    for entry in reversed(state.get("transcript", [])):
        if entry["role"] == "guest" and entry["speaker"] != exclude:
            return entry
    return None


def render_recent_transcript(state: ShowState, limit: int = 8) -> str:
    lines = []
    for entry in state.get("transcript", [])[-limit:]:
        lines.append(f"[Round {entry['round']}] {entry['speaker_name']}: {entry['text']}")
    return "\n".join(lines)
