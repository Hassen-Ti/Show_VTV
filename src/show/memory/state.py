"""État partagé du show : le monde commun que tous les agents lisent/écrivent.

Write-contract (qui écrit quoi)
--------------------------------
Invité (guest nodes)
  Lit  : ``transcript``, ``minds``, ``turn``, ``pending_audience_question``
  Écrit : ``minds[leur_id]`` seulement (delta fusionné via ``merge_minds``),
          ``turn``, une entrée ``transcript``

Animateur (host / moderator)
  Lit  : ``tension``, ``stance_history``, ``transcript``
  Écrit : ``current_speaker``, ``moderator_notes``, ``transcript``,
          ``pending_audience_question``

Moteur — ``update_shared_state`` (``memory.update``)
  Lit  : ``minds``, ``transcript`` (entrées du round courant), ``turn_index``,
         ``stance_history``
  Écrit :
    - ``tension``        — recalculée via ``mind.compute_tension``
    - ``stance_history`` — append de la stance courante de chaque agent présent
    - ``minds``          — ``mind.decay`` appliqué à chaque invité **uniquement
      quand le round est complet** (``turn_index % 2 == 0``)

Champs optionnels (``ShowState`` est ``total=False`` ; ne pas renommer/retirer
les champs existants). Nouveaux champs = optionnels seulement.

Helpers de persistance inter-épisode
------------------------------------
``snapshot_minds`` / ``seed_minds_from_prior`` / ``initial_show_state(..., prior_minds=)``
permettent de porter stance / conviction / beliefs / grudges d'un épisode à
l'autre **sans** casser le TypedDict ni exiger de storage dans ce module.
L'affect éphémère (valence, arousal, monologue) est réinitialisé au seed.
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


class _MindStateRequired(TypedDict):
    stance: float          # opinion courante [-1, 1]
    conviction: float      # certitude [0, 1]
    valence: float         # humeur [-1, 1]
    arousal: float         # excitation [0, 1]
    beliefs: list[str]     # faits acceptés (mémoire)
    grudges: list[str]     # attaques subies non répondues
    inner_monologue: str   # pensée privée du dernier tour


class MindState(_MindStateRequired, total=False):
    """État mental d'un agent.

    Champs requis : stance, conviction, valence, arousal, beliefs, grudges,
    inner_monologue. Optionnel :
    - ``carried_over`` : True si la mind a été seedée depuis un snapshot
      d'épisode précédent (marque purement informative ; le moteur l'ignore).
    """

    carried_over: bool


def merge_minds(
    left: dict[str, MindState] | None,
    right: dict[str, MindState] | None,
) -> dict[str, MindState]:
    """Reducer LangGraph : fusionne les deltas ``minds`` (clé = agent_id).

    Les invités doivent renvoyer seulement ``{leur_id: mind}`` ; le moteur
    peut renvoyer un sous-ensemble après ``decay``.
    """
    return {**(left or {}), **(right or {})}


class ShowState(TypedDict, total=False):
    topic: str
    round: int
    max_rounds: int
    turn_index: int
    transcript: Annotated[list[TranscriptEntry], operator.add]
    current_speaker: str
    minds: Annotated[dict[str, MindState], merge_minds]
    tension: float
    stance_history: dict[str, list[float]]
    moderator_notes: Annotated[list[str], operator.add]
    turn: dict[str, Any]  # scratch du tour courant (claim, angle, evidence, tactic…)
    # Question spectateur drainée en interjection ; consommée par le prochain listen.
    pending_audience_question: str
    # Éphémère : sortie du nœud ``decide_after_update`` (câblage compositeur).
    next_moderator_action: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


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


def snapshot_minds(minds: dict[str, MindState]) -> dict[str, MindState]:
    """Copie profonde JSON-serializable des minds (hook persistance inter-épisode).

    Ne mute pas l'entrée. Les listes ``beliefs`` / ``grudges`` sont re-créées.
    Dictionnaire vide → dictionnaire vide.
    """
    out: dict[str, MindState] = {}
    for agent_id, mind in (minds or {}).items():
        snap: MindState = MindState(
            stance=float(mind["stance"]),
            conviction=float(mind["conviction"]),
            valence=float(mind["valence"]),
            arousal=float(mind["arousal"]),
            beliefs=list(mind.get("beliefs", [])),
            grudges=list(mind.get("grudges", [])),
            inner_monologue=str(mind.get("inner_monologue", "")),
        )
        if "carried_over" in mind:
            snap["carried_over"] = bool(mind["carried_over"])
        out[agent_id] = snap
    return out


def seed_minds_from_prior(
    guests: list[PersonaVector],
    prior: dict[str, MindState] | None = None,
) -> dict[str, MindState]:
    """Construit les minds d'un nouvel épisode.

    Sans ``prior`` : équivalent à ``{g.agent_id: initial_mind(g) for g in guests}``.
    Avec ``prior`` : pour chaque invité présent dans le snapshot, porte
    ``stance``, ``conviction``, ``beliefs``, ``grudges`` ; réinitialise valence
    (baseline), arousal (0.2) et ``inner_monologue``. Marque ``carried_over``.
    Les agent_id absents du prior restent à l'état initial.
    """
    minds = {g.agent_id: initial_mind(g) for g in guests}
    if not prior:
        return minds
    for guest in guests:
        prev = prior.get(guest.agent_id)
        if prev is None:
            continue
        seeded: MindState = MindState(
            stance=_clamp(float(prev["stance"]), -1.0, 1.0),
            conviction=_clamp(float(prev["conviction"]), 0.1, 1.0),
            valence=guest.affective_baseline,
            arousal=0.2,
            beliefs=list(prev.get("beliefs", [])),
            grudges=list(prev.get("grudges", [])),
            inner_monologue="",
            carried_over=True,
        )
        minds[guest.agent_id] = seeded
    return minds


def initial_show_state(
    topic: str,
    guests: list[PersonaVector],
    max_rounds: int,
    *,
    prior_minds: dict[str, MindState] | None = None,
) -> ShowState:
    """État initial d'un épisode.

    ``prior_minds`` (optionnel) : snapshot d'un épisode précédent
    (voir ``snapshot_minds``) pour enchaîner la mémoire durable.
    """
    minds = seed_minds_from_prior(guests, prior_minds)
    return ShowState(
        topic=topic,
        round=0,
        max_rounds=max_rounds,
        turn_index=0,
        transcript=[],
        current_speaker="",
        minds=minds,
        tension=0.0,
        stance_history={g.agent_id: [minds[g.agent_id]["stance"]] for g in guests},
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
