"""Feature invités : personas, nœuds cognitifs, sous-graphe, presets."""

from show.guests.personas.registry import DOMAINS, PERSONALITIES, make_guest
from show.guests.personas.vector import PersonaVector, validate
from show.guests.subgraph import build_guest_subgraph

__all__ = [
    "DOMAINS",
    "PERSONALITIES",
    "PersonaVector",
    "build_guest_subgraph",
    "make_guest",
    "validate",
]
