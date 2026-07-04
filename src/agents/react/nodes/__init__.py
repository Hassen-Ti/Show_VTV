"""Nœuds du graphe débatteur ONPC (fonctions LangGraph)."""

from agents.react.nodes.character import apply_character
from agents.react.nodes.draft import draft_argument
from agents.react.nodes.frame import choose_frame
from agents.react.nodes.parse import parse_opponent
from agents.react.nodes.polish import polish_onpc
from agents.react.nodes.search import search_web
from agents.react.nodes.tactic import select_tactic

__all__ = [
    "parse_opponent",
    "choose_frame",
    "search_web",
    "select_tactic",
    "draft_argument",
    "apply_character",
    "polish_onpc",
]
