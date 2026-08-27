"""Personas du show : schéma PersonaVector + registre personnalité × domaine."""

from show.guests.personas.registry import (
    DOMAINS,
    MODERATOR_PERSONA,
    PERSONALITIES,
    make_guest,
)
from show.guests.personas.vector import SHOW_TACTICS, PersonaVector, validate

__all__ = [
    "DOMAINS",
    "MODERATOR_PERSONA",
    "PERSONALITIES",
    "PersonaVector",
    "SHOW_TACTICS",
    "make_guest",
    "validate",
]
