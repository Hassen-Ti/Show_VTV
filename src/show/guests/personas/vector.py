"""Schéma PersonaVector : une personne (personnalité × domaine), pas une position."""

from __future__ import annotations

from dataclasses import dataclass, fields

# Canonical : ``show.memory.traits`` — réexport compat pour guests / benchmarks.
from show.memory.traits import AGGRESSIVE_TACTICS

# Tactiques disponibles sur le plateau (le registre en attribue un sous-ensemble
# par personnalité ; `strategize` ne peut choisir qu'à l'intérieur de ce sous-ensemble).
SHOW_TACTICS = frozenset(
    {
        "clash",
        "contradiction",
        "pivot",
        "pivot_future",
        "moral_attack",
        "expose_hypocrisy",
        "dismiss_fear",
        "concede_then_refute",
        "reframe",
    }
)

# Nœuds cognitifs implémentés dans show.nodes (registre de factories).
COGNITIVE_NODES = frozenset(
    {
        "listen",
        "verify_facts",
        "hypothesize",
        "recall_precedent",
        "build_analogy",
        "reframe_concept",
        "find_contradiction",
        "recall_anecdote",
        "narrative_frame",
        "quantify",
        "model_tradeoff",
        "strategize",
        "plan",
        "reflect",
        "revise_draft",
        "critic_verify",
        "self_correct",
        "recall_memory",
        "supervisor_route",
        "parallel_gather",
    }
)

EVIDENCE_STYLES = frozenset(
    {"empirical", "precedent", "dialectic", "narrative", "formal"}
)


@dataclass(frozen=True)
class PersonaVector:
    # identité
    name: str
    agent_id: str
    personality: str
    domain: str
    specialization: str
    architecture_id: str
    # cognition — topologie LangGraph (dérivée de architecture_id + domaine)
    cognitive_sequence: tuple[str, ...]
    evidence_style: str
    # caractère — modulation des prompts et des algorithmes
    affective_baseline: float
    arousal_gain: float
    tactics: tuple[str, ...]
    concession_rate: float
    stubbornness: float
    opener: str
    sentence_max: int
    temperature_facts: float
    temperature_voice: float
    forbidden: tuple[str, ...]
    # opinion initiale sur le sujet
    initial_stance: float
    initial_conviction: float


def _check_range(errors: list[str], label: str, value: float, lo: float, hi: float) -> None:
    if not (lo <= value <= hi):
        errors.append(f"{label}={value} hors bornes [{lo}, {hi}]")


def validate(vector: PersonaVector) -> None:
    """Lève ValueError sur toute incohérence — aucun fallback silencieux."""
    errors: list[str] = []

    for field in ("name", "agent_id", "personality", "domain", "specialization", "opener"):
        if not getattr(vector, field):
            errors.append(f"champ vide: {field}")

    if not vector.cognitive_sequence:
        errors.append("cognitive_sequence vide")
    unknown_nodes = set(vector.cognitive_sequence) - COGNITIVE_NODES - frozenset(
        {"concede_then_refute", "draft", "voice", "deliver"}
    )
    if unknown_nodes:
        errors.append(f"nœuds cognitifs inconnus: {sorted(unknown_nodes)}")
    if vector.cognitive_sequence:
        valid_starts = ("listen", "recall_memory")
        if vector.cognitive_sequence[0] not in valid_starts:
            errors.append(
                f"cognitive_sequence doit commencer par {valid_starts}, "
                f"reçu {vector.cognitive_sequence[0]!r}"
            )
    if vector.cognitive_sequence and vector.cognitive_sequence[-1] != "strategize":
        errors.append("cognitive_sequence doit finir par 'strategize'")

    if not vector.architecture_id:
        errors.append("champ vide: architecture_id")

    if vector.evidence_style not in EVIDENCE_STYLES:
        errors.append(f"evidence_style inconnu: {vector.evidence_style}")

    if not vector.tactics:
        errors.append("tactics vide")
    unknown_tactics = set(vector.tactics) - SHOW_TACTICS
    if unknown_tactics:
        errors.append(f"tactiques inconnues: {sorted(unknown_tactics)}")

    _check_range(errors, "affective_baseline", vector.affective_baseline, -1.0, 1.0)
    _check_range(errors, "arousal_gain", vector.arousal_gain, 0.0, 1.0)
    _check_range(errors, "concession_rate", vector.concession_rate, 0.0, 1.0)
    _check_range(errors, "stubbornness", vector.stubbornness, 0.0, 1.0)
    _check_range(errors, "initial_stance", vector.initial_stance, -1.0, 1.0)
    _check_range(errors, "initial_conviction", vector.initial_conviction, 0.0, 1.0)
    if vector.sentence_max < 1:
        errors.append(f"sentence_max={vector.sentence_max} doit être >= 1")

    if errors:
        raise ValueError(f"PersonaVector invalide ({vector.name!r}): " + "; ".join(errors))


PERSONA_FIELDS = tuple(f.name for f in fields(PersonaVector))
