"""Présets d'invités pour l'UI (personnalité × domaine × spécialisation × stance)."""

from __future__ import annotations

from dataclasses import dataclass

from show.guests.personas.registry import make_guest
from show.guests.personas.vector import PersonaVector


@dataclass(frozen=True)
class ShowPreset:
    key: str
    label: str
    topic: str
    theme_hint: str
    guest_a: tuple[str, str, str, float]  # personality, domain, specialization, stance
    guest_b: tuple[str, str, str, float]


SHOW_PRESETS: dict[str, ShowPreset] = {
    "": ShowPreset(
        key="",
        label="Débat libre",
        topic="Devons-nous faire confiance à l'IA pour les diagnostics médicaux?",
        theme_hint="Intelligence artificielle et société",
        guest_a=("provocateur", "physicien", "intelligence artificielle", 0.8),
        guest_b=("diplomate", "philosophe", "éthique des techniques", -0.6),
    ),
    "economie_emplois": ShowPreset(
        key="economie_emplois",
        label="Économie & emplois",
        topic="L'IA doit-elle remplacer les emplois humains?",
        theme_hint="IA, emploi et productivité",
        guest_a=("provocateur", "economiste", "IA et emploi", 0.85),
        guest_b=("diplomate", "economiste", "transition sociale", -0.75),
    ),
    "education_ia": ShowPreset(
        key="education_ia",
        label="Éducation & IA",
        topic="L'IA peut-elle remplacer les professeurs?",
        theme_hint="Éducation et intelligence artificielle",
        guest_a=("cerebral", "philosophe", "pédagogie numérique", 0.7),
        guest_b=("diplomate", "philosophe", "humanités", -0.65),
    ),
    "sante_diagnostic": ShowPreset(
        key="sante_diagnostic",
        label="Santé & diagnostic",
        topic="Faut-il faire confiance aux diagnostics IA?",
        theme_hint="Santé et intelligence artificielle",
        guest_a=("provocateur", "physicien", "imagerie médicale", 0.8),
        guest_b=("diplomate", "philosophe", "éthique médicale", -0.7),
    ),
    "surveillance_securite": ShowPreset(
        key="surveillance_securite",
        label="Surveillance & IA",
        topic="La surveillance par IA est-elle acceptable?",
        theme_hint="Sécurité, libertés et IA",
        guest_a=("cerebral", "historien", "sécurité publique", 0.6),
        guest_b=("provocateur", "philosophe", "libertés individuelles", -0.8),
    ),
    "art_creation": ShowPreset(
        key="art_creation",
        label="Création artistique",
        topic="L'art créé par IA a-t-il de la valeur?",
        theme_hint="Création artistique et IA",
        guest_a=("provocateur", "ecrivain", "art génératif", 0.75),
        guest_b=("cerebral", "philosophe", "esthétique", -0.7),
    ),
}

PRESET_KEYS = ["", "economie_emplois", "education_ia", "sante_diagnostic", "surveillance_securite", "art_creation"]


def get_preset(key: str) -> ShowPreset:
    return SHOW_PRESETS.get(key, SHOW_PRESETS[""])


def build_guests(preset_key: str) -> tuple[PersonaVector, PersonaVector]:
    preset = get_preset(preset_key)
    a = preset.guest_a
    b = preset.guest_b
    guest_a = make_guest(a[0], a[1], a[2], a[3], agent_id="guest_a")
    guest_b = make_guest(b[0], b[1], b[2], b[3], agent_id="guest_b")
    return guest_a, guest_b


def guest_names(preset_key: str) -> dict[str, str]:
    guest_a, guest_b = build_guests(preset_key)
    return {"left": guest_a.name, "right": guest_b.name}
