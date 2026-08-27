"""Shim : ``show.personas.registry`` → ``show.guests.personas.registry``."""

from show.guests.personas.registry import *  # noqa: F403
from show.host.persona import MODERATOR_PERSONA, ModeratorPersona

__all__ = [
    "DOMAINS",
    "MODERATOR_PERSONA",
    "ModeratorPersona",
    "PERSONALITIES",
    "make_guest",
    "make_guest_with_architecture",
    "persona_style_hints",
]
