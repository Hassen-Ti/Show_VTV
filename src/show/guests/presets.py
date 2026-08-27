"""Présets d'invités pour l'UI (personnalité × domaine × spécialisation × stance).

Chaque preset décrit un duel : ``guest_a`` / ``guest_b`` via ``GuestSpec``.
``PRESET_KEYS`` est la liste ordonnée exposée à l'UI ; ``SHOW_PRESETS`` est la
source de vérité (clé ``""`` = débat libre par défaut).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from show.guests.personas.registry import make_guest
from show.guests.personas.vector import PersonaVector


class GuestSpec(NamedTuple):
    """Spécification d'un invité de preset (indexable comme un tuple legacy)."""

    personality: str
    domain: str
    specialization: str
    stance: float


@dataclass(frozen=True)
class ShowPreset:
    key: str
    label: str
    topic: str
    theme_hint: str
    guest_a: GuestSpec
    guest_b: GuestSpec


SHOW_PRESETS: dict[str, ShowPreset] = {
    "": ShowPreset(
        key="",
        label="Débat libre",
        topic="Devons-nous faire confiance à l'IA pour les diagnostics médicaux?",
        theme_hint="Intelligence artificielle et société",
        guest_a=GuestSpec("provocateur", "physicien", "intelligence artificielle", 0.8),
        guest_b=GuestSpec("diplomate", "philosophe", "éthique des techniques", -0.6),
    ),
    "economie_emplois": ShowPreset(
        key="economie_emplois",
        label="Économie & emplois",
        topic="L'IA doit-elle remplacer les emplois humains?",
        theme_hint="IA, emploi et productivité",
        guest_a=GuestSpec("provocateur", "economiste", "IA et emploi", 0.85),
        guest_b=GuestSpec("diplomate", "economiste", "transition sociale", -0.75),
    ),
    "education_ia": ShowPreset(
        key="education_ia",
        label="Éducation & IA",
        topic="L'IA peut-elle remplacer les professeurs?",
        theme_hint="Éducation et intelligence artificielle",
        guest_a=GuestSpec("cerebral", "philosophe", "pédagogie numérique", 0.7),
        guest_b=GuestSpec("diplomate", "philosophe", "humanités", -0.65),
    ),
    "sante_diagnostic": ShowPreset(
        key="sante_diagnostic",
        label="Santé & diagnostic",
        topic="Faut-il faire confiance aux diagnostics IA?",
        theme_hint="Santé et intelligence artificielle",
        guest_a=GuestSpec("provocateur", "physicien", "imagerie médicale", 0.8),
        guest_b=GuestSpec("diplomate", "philosophe", "éthique médicale", -0.7),
    ),
    "surveillance_securite": ShowPreset(
        key="surveillance_securite",
        label="Surveillance & IA",
        topic="La surveillance par IA est-elle acceptable?",
        theme_hint="Sécurité, libertés et IA",
        guest_a=GuestSpec("cerebral", "historien", "sécurité publique", 0.6),
        guest_b=GuestSpec("provocateur", "philosophe", "libertés individuelles", -0.8),
    ),
    "art_creation": ShowPreset(
        key="art_creation",
        label="Création artistique",
        topic="L'art créé par IA a-t-il de la valeur?",
        theme_hint="Création artistique et IA",
        guest_a=GuestSpec("provocateur", "ecrivain", "art génératif", 0.75),
        guest_b=GuestSpec("cerebral", "philosophe", "esthétique", -0.7),
    ),
}

# Ordre UI ; doit rester aligné sur les clés de ``SHOW_PRESETS``.
PRESET_KEYS = ["", "economie_emplois", "education_ia", "sante_diagnostic", "surveillance_securite", "art_creation"]


def get_preset(key: str) -> ShowPreset:
    return SHOW_PRESETS.get(key, SHOW_PRESETS[""])


def _guest_from_spec(spec: GuestSpec, agent_id: str) -> PersonaVector:
    return make_guest(
        spec.personality,
        spec.domain,
        spec.specialization,
        spec.stance,
        agent_id=agent_id,
    )


def build_guests(preset_key: str) -> tuple[PersonaVector, PersonaVector]:
    preset = get_preset(preset_key)
    return (
        _guest_from_spec(preset.guest_a, "guest_a"),
        _guest_from_spec(preset.guest_b, "guest_b"),
    )


def guest_names(preset_key: str) -> dict[str, str]:
    guest_a, guest_b = build_guests(preset_key)
    return {"left": guest_a.name, "right": guest_b.name}
