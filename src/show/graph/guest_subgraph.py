"""Sous-graphe invité : la séquence cognitive du persona devient une topologie.

Deux invités de domaines différents ne traversent pas les mêmes nœuds :
le physicien vérifie les faits avant d'hypothétiser, le philosophe recadre le
concept avant de chercher la contradiction, etc. La concession est une branche
conditionnelle pilotée par le mind (``turn.must_concede``).
"""

from __future__ import annotations

from itertools import pairwise

from langgraph.graph import END, START, StateGraph

from show.context import ShowContext
from show.nodes import NODE_REGISTRY
from show.personas.vector import PersonaVector, validate
from show.state import ShowState


def route_concession(state: ShowState) -> str:
    return "concede_then_refute" if state["turn"].get("must_concede") else "draft"


def build_guest_subgraph(persona: PersonaVector):
    """Compile la ``cognitive_sequence`` du persona en sous-graphe LangGraph."""
    validate(persona)
    graph = StateGraph(ShowState, context_schema=ShowContext)

    sequence = persona.cognitive_sequence  # commence par listen, finit par strategize
    for name in sequence:
        graph.add_node(name, NODE_REGISTRY[name](persona))
    for name in ("concede_then_refute", "draft", "voice", "deliver"):
        graph.add_node(name, NODE_REGISTRY[name](persona))

    graph.add_edge(START, sequence[0])
    for upstream, downstream in pairwise(sequence):
        graph.add_edge(upstream, downstream)

    # Branche de caractère : concéder avant de contre-attaquer.
    graph.add_conditional_edges(
        sequence[-1],
        route_concession,
        {"concede_then_refute": "concede_then_refute", "draft": "draft"},
    )
    graph.add_edge("concede_then_refute", "draft")
    graph.add_edge("draft", "voice")
    graph.add_edge("voice", "deliver")
    graph.add_edge("deliver", END)
    return graph.compile()
