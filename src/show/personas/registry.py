"""Matrice personnalité × domaine et fabrique d'invités.

La personnalité pilote le caractère (émotions, tactiques, résistance) ;
le domaine pilote la cognition (séquence de nœuds, style de preuve, lexique).
"""

from __future__ import annotations

from dataclasses import dataclass

from show.personas.vector import PersonaVector, validate

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
    },
}

# Cognition : comment la personne pense — séquence de nœuds du graphe.
DOMAINS: dict[str, dict] = {
    "physicien": {
        "cognitive_sequence": ("listen", "verify_facts", "hypothesize", "strategize"),
        "evidence_style": "empirical",
        "domain_label": "physicien",
        "lexicon_hint": "ordres de grandeur, incertitudes, données mesurées, protocole",
    },
    "historien": {
        "cognitive_sequence": ("listen", "recall_precedent", "build_analogy", "strategize"),
        "evidence_style": "precedent",
        "domain_label": "historien",
        "lexicon_hint": "précédents, périodes, causes longues, archives",
    },
    "philosophe": {
        "cognitive_sequence": ("listen", "reframe_concept", "find_contradiction", "strategize"),
        "evidence_style": "dialectic",
        "domain_label": "philosophe",
        "lexicon_hint": "concepts, présupposés, distinctions, contradictions internes",
    },
    "ecrivain": {
        "cognitive_sequence": ("listen", "recall_anecdote", "narrative_frame", "strategize"),
        "evidence_style": "narrative",
        "domain_label": "écrivain",
        "lexicon_hint": "récits, personnages, images, détails sensibles",
    },
    "economiste": {
        "cognitive_sequence": ("listen", "quantify", "model_tradeoff", "strategize"),
        "evidence_style": "formal",
        "domain_label": "économiste",
        "lexicon_hint": "coûts, incitations, arbitrages, élasticités, agrégats",
    },
}

DEFAULT_FORBIDDEN = ("insulte", "injure", "attaque personnelle")


def make_guest(
    personality: str,
    domain: str,
    specialization: str,
    stance: float,
    *,
    agent_id: str,
    name: str = "",
    conviction: float = 0.8,
) -> PersonaVector:
    """Compose un invité personnalité × domaine. Lève ValueError sur clé inconnue."""
    if personality not in PERSONALITIES:
        raise ValueError(
            f"personnalité inconnue: {personality!r} (choix: {sorted(PERSONALITIES)})"
        )
    if domain not in DOMAINS:
        raise ValueError(f"domaine inconnu: {domain!r} (choix: {sorted(DOMAINS)})")

    p = PERSONALITIES[personality]
    d = DOMAINS[domain]
    vector = PersonaVector(
        name=name or f"{personality.capitalize()} {d['domain_label']}",
        agent_id=agent_id,
        personality=personality,
        domain=domain,
        specialization=specialization,
        cognitive_sequence=tuple(d["cognitive_sequence"]),
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


def persona_style_hints(vector: PersonaVector) -> tuple[str, str]:
    """(voice_hint, lexicon_hint) pour les prompts — dérivés du registre."""
    return (
        PERSONALITIES[vector.personality]["voice_hint"],
        DOMAINS[vector.domain]["lexicon_hint"],
    )


@dataclass(frozen=True)
class ModeratorPersona:
    name: str
    agent_id: str
    style: str
    signature: str
    interject_threshold: float  # tension au-delà de laquelle il s'interpose
    sentence_max: int
    temperature: float


MODERATOR_PERSONA = ModeratorPersona(
    name="L'Animateur",
    agent_id="moderator",
    style=(
        "animateur de débat TV français, incisif mais élégant : il résume, "
        "confronte les invités à leurs contradictions et protège le rythme du plateau"
    ),
    signature="On continue, restez avec nous !",
    interject_threshold=0.65,
    sentence_max=2,
    temperature=0.8,
)
