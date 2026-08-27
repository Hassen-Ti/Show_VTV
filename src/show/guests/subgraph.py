"""Sous-graphe invité : topologie pilotée par ``architecture_id`` (patterns publiés).

Chaque persona embarque une architecture agentique (ReAct, Reflexion, Plan-and-Execute…)
et un domaine qui choisit les nœuds de preuve / pensée spécialisés via
``domain_worker_nodes`` (registre — pas de table dupliquée ici).
"""

from __future__ import annotations

from itertools import pairwise

from langgraph.graph import END, START, StateGraph

from show.runtime.context import ShowContext
from show.guests.nodes import NODE_REGISTRY
from show.guests.nodes.factories import route_critic_gate, route_supervisor
from show.guests.personas.trace import make_traced_node
from show.guests.personas.architectures import get_architecture
from show.guests.personas.registry import domain_worker_nodes
from show.guests.personas.vector import PersonaVector, validate
from show.memory.state import ShowState


def route_concession(state: ShowState) -> str:
    return "concede_then_refute" if state["turn"].get("must_concede") else "draft"


def _register_nodes(graph: StateGraph, persona: PersonaVector, names: set[str]) -> None:
    delivery = {"concede_then_refute", "draft", "voice", "deliver"}
    for name in names | delivery:
        if name not in graph.nodes:
            graph.add_node(name, make_traced_node(persona, name, NODE_REGISTRY[name](persona)))


def _attach_delivery_pipeline(graph: StateGraph, persona: PersonaVector, spec) -> None:
    """Suffixe commun : strategize → concession → draft → [post] → voice → deliver."""
    graph.add_conditional_edges(
        "strategize",
        route_concession,
        {"concede_then_refute": "concede_then_refute", "draft": "draft"},
    )
    graph.add_edge("concede_then_refute", "draft")

    if spec.post_draft == "reflect":
        graph.add_edge("draft", "reflect")
        graph.add_edge("reflect", "revise_draft")
        graph.add_edge("revise_draft", "voice")
    elif spec.post_draft == "self_correct":
        graph.add_edge("draft", "self_correct")
        graph.add_edge("self_correct", "voice")
    elif spec.post_draft == "critic_gate":
        graph.add_edge("draft", "critic_verify")
        graph.add_conditional_edges(
            "critic_verify",
            route_critic_gate,
            {"voice": "voice", "revise_draft": "revise_draft"},
        )
        graph.add_edge("revise_draft", "voice")
    else:
        graph.add_edge("draft", "voice")

    graph.add_edge("voice", "deliver")
    graph.add_edge("deliver", END)


def build_guest_subgraph(persona: PersonaVector):
    """Compile ``architecture_id`` + domaine en sous-graphe LangGraph."""
    validate(persona)
    spec = get_architecture(persona.architecture_id)
    graph = StateGraph(ShowState, context_schema=ShowContext)

    path = list(persona.cognitive_sequence)
    if "strategize" not in path:
        path.append("strategize")

    worker_evidence, worker_think = domain_worker_nodes(persona.domain)

    extra = {
        "concede_then_refute", "draft", "voice", "deliver",
        "reflect", "revise_draft", "critic_verify", "self_correct",
        worker_evidence, worker_think, "reframe_concept", "find_contradiction",
    }
    _register_nodes(graph, persona, set(path) | extra)

    if spec.uses_supervisor:
        graph.add_edge(START, "listen")
        graph.add_edge("listen", "supervisor_route")
        graph.add_conditional_edges(
            "supervisor_route",
            route_supervisor,
            {
                "evidence": worker_evidence,
                "dialectic": "reframe_concept",
            },
        )
        graph.add_edge(worker_evidence, worker_think)
        graph.add_edge("reframe_concept", "find_contradiction")
        graph.add_edge("find_contradiction", "strategize")
        graph.add_edge(worker_think, "strategize")
    else:
        graph.add_edge(START, path[0])
        for upstream, downstream in pairwise(path):
            graph.add_edge(upstream, downstream)

    _attach_delivery_pipeline(graph, persona, spec)
    return graph.compile()
