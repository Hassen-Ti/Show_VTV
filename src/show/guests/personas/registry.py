"""Matrice personnalité × domaine × architecture agentique.

La personnalité pilote le caractère (émotions, tactiques, résistance) ;
le domaine pilote le lexique et le style de preuve ;
l'architecture pilote la topologie LangGraph (workflow agentique publié).
"""

from __future__ import annotations

from show.guests.personas.architectures import (
    ARCHITECTURE_IDS,
    PERSONALITY_ARCHITECTURE,
    cognitive_sequence_for,
    get_architecture,
)
from show.guests.personas.vector import PersonaVector, validate

# Caractère : comment la personne réagit et attaque.
PERSONALITIES: dict[str, dict] = {
    "provocateur": {
        "affective_baseline": 0.1,
        "arousal_gain": 0.8,
        "tactics": ("clash", "expose_hypocrisy", "moral_attack"),
        "concession_rate": 0.05,
        "stubbornness": 0.9,
        "opener": "Soyons sérieux :",
        "sentence_max": 2,
        "temperature_facts": 0.4,
        "temperature_voice": 1.3,
        "voice_hint": "cassant, ironique, cherche le clash frontal",
        "architecture_id": "react",
        "conclave_role": "Le Flux",
    },
    "diplomate": {
        "affective_baseline": 0.3,
        "arousal_gain": 0.3,
        "tactics": ("concede_then_refute", "pivot", "dismiss_fear"),
        "concession_rate": 0.35,
        "stubbornness": 0.4,
        "opener": "Je vous rejoins sur un point, mais",
        "sentence_max": 3,
        "temperature_facts": 0.4,
        "temperature_voice": 1.0,
        "voice_hint": "posé, chaleureux, désamorce puis retourne l'argument",
        "architecture_id": "reflexion",
        "conclave_role": "Le Protocole",
    },
    "cerebral": {
        "affective_baseline": 0.0,
        "arousal_gain": 0.45,
        "tactics": ("contradiction", "reframe", "pivot_future"),
        "concession_rate": 0.15,
        "stubbornness": 0.7,
        "opener": "Reprenons les termes du problème :",
        "sentence_max": 3,
        "temperature_facts": 0.3,
        "temperature_voice": 0.9,
        "voice_hint": "précis, froid, démonte la logique pièce par pièce",
        "architecture_id": "plan_execute",
        "conclave_role": "L'Archive",
    },
}

# Domaine : lexique + style de preuve (plus de séquence cognitive figée).
DOMAINS: dict[str, dict] = {
    "physicien": {
        "evidence_style": "empirical",
        "domain_label": "physicien",
        "lexicon_hint": "ordres de grandeur, incertitudes, données mesurées, protocole",
        "think_node": "hypothesize",
        "evidence_node": "verify_facts",
    },
    "historien": {
        "evidence_style": "precedent",
        "domain_label": "historien",
        "lexicon_hint": "précédents, périodes, causes longues, archives",
        "think_node": "build_analogy",
        "evidence_node": "recall_precedent",
    },
    "philosophe": {
        "evidence_style": "dialectic",
        "domain_label": "philosophe",
        "lexicon_hint": "concepts, présupposés, distinctions, contradictions internes",
        "think_node": "find_contradiction",
        "evidence_node": "reframe_concept",
    },
    "ecrivain": {
        "evidence_style": "narrative",
        "domain_label": "écrivain",
        "lexicon_hint": "récits, personnages, images, détails sensibles",
        "think_node": "narrative_frame",
        "evidence_node": "recall_anecdote",
    },
    "economiste": {
        "evidence_style": "formal",
        "domain_label": "économiste",
        "lexicon_hint": "coûts, incitations, arbitrages, élasticités, agrégats",
        "think_node": "model_tradeoff",
        "evidence_node": "quantify",
    },
}

DEFAULT_FORBIDDEN = ("insulte", "injure", "attaque personnelle")


def _resolve_cognitive_sequence(
    architecture_id: str,
    domain: str,
    *,
    override: str | None = None,
) -> tuple[str, ...]:
    """Construit la séquence cognitive : architecture + nœuds domaine."""
    if override:
        return cognitive_sequence_for(override)

    spec = get_architecture(architecture_id)
    d = DOMAINS[domain]
    evidence = d["evidence_node"]
    think = d["think_node"]

    if spec.uses_supervisor:
        return ("listen", "supervisor_route", "strategize")

    path: list[str] = []
    for node in spec.cognitive_path:
        if node == "verify_facts":
            path.append(evidence)
        elif node == "hypothesize":
            path.append(think)
        else:
            path.append(node)

    if "strategize" not in path:
        path.append("strategize")
    return tuple(path)


def make_guest(
    personality: str,
    domain: str,
    specialization: str,
    stance: float,
    *,
    agent_id: str,
    name: str = "",
    conviction: float = 0.8,
    architecture_id: str | None = None,
) -> PersonaVector:
    """Compose un invité personnalité × domaine × architecture."""
    if personality not in PERSONALITIES:
        raise ValueError(
            f"personnalité inconnue: {personality!r} (choix: {sorted(PERSONALITIES)})"
        )
    if domain not in DOMAINS:
        raise ValueError(f"domaine inconnu: {domain!r} (choix: {sorted(DOMAINS)})")

    p = PERSONALITIES[personality]
    d = DOMAINS[domain]
    arch = architecture_id or p["architecture_id"]
    if arch not in ARCHITECTURE_IDS:
        raise ValueError(f"architecture inconnue: {arch!r}")

    cog_seq = _resolve_cognitive_sequence(arch, domain)

    vector = PersonaVector(
        name=name or f"{personality.capitalize()} {d['domain_label']}",
        agent_id=agent_id,
        personality=personality,
        domain=domain,
        specialization=specialization,
        architecture_id=arch,
        cognitive_sequence=cog_seq,
        evidence_style=d["evidence_style"],
        affective_baseline=p["affective_baseline"],
        arousal_gain=p["arousal_gain"],
        tactics=tuple(p["tactics"]),
        concession_rate=p["concession_rate"],
        stubbornness=p["stubbornness"],
        opener=p["opener"],
        sentence_max=p["sentence_max"],
        temperature_facts=p["temperature_facts"],
        temperature_voice=p["temperature_voice"],
        forbidden=DEFAULT_FORBIDDEN,
        initial_stance=stance,
        initial_conviction=conviction,
    )
    validate(vector)
    return vector


def make_guest_with_architecture(
    personality: str,
    domain: str,
    specialization: str,
    stance: float,
    architecture_id: str,
    *,
    agent_id: str,
    name: str = "",
) -> PersonaVector:
    """Fabrique un invité en forçant une architecture (benchmark / A-B test)."""
    return make_guest(
        personality,
        domain,
        specialization,
        stance,
        agent_id=agent_id,
        name=name,
        architecture_id=architecture_id,
    )


def persona_style_hints(vector: PersonaVector) -> tuple[str, str]:
    """(voice_hint, lexicon_hint) pour les prompts — dérivés du registre."""
    return (
        PERSONALITIES[vector.personality]["voice_hint"],
        DOMAINS[vector.domain]["lexicon_hint"],
    )

# Compat : animateur vit dans ``show.host`` ; réexport pour anciens imports.
from show.host.persona import MODERATOR_PERSONA, ModeratorPersona  # noqa: E402
