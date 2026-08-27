"""Compositeur figé : câble host + guests + memory. Ne contient plus de logique métier.

Topologie :
    START → moderator_open → moderator_allocate_floor
        → (guest_a | guest_b) → update_shared_state
        → (moderator_allocate_floor | moderator_interject | moderator_conclude)
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from openai import OpenAI

from config.show_config import SHOW_CONFIG
from show.guests.personas.vector import PersonaVector
from show.guests.subgraph import build_guest_subgraph
from show.host.nodes import (
    make_moderator_allocate_floor,
    make_moderator_conclude,
    make_moderator_interject,
    make_moderator_open,
    make_route_after_allocate,
    make_route_after_update,
)
from show.host.persona import MODERATOR_PERSONA, ModeratorPersona
from show.memory.state import ShowState, initial_show_state
from show.memory.update import make_update_shared_state
from show.runtime.context import (
    EarpiecePeek,
    EarpiecePoll,
    EmitCallback,
    ShowContext,
)


def _make_guest_node(persona: PersonaVector):
    """Enveloppe le sous-graphe invité pour ne renvoyer que le delta d'état.

    Le transcript porte un reducer ``operator.add`` : renvoyer l'état final du
    sous-graphe tel quel ré-appendrait les entrées héritées du parent.
    """
    compiled = build_guest_subgraph(persona)

    def guest_node(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        inherited = len(state["transcript"])
        out = compiled.invoke(state, context=runtime.context)
        delta = {
            "transcript": out["transcript"][inherited:],
            "minds": out["minds"],
            "turn": out["turn"],
        }
        if "pending_audience_question" in out:
            delta["pending_audience_question"] = out["pending_audience_question"]
        return delta

    return guest_node


def build_show_graph(
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    moderator: ModeratorPersona = MODERATOR_PERSONA,
    *,
    peek_earpiece: Optional[EarpiecePeek] = None,
):
    graph = StateGraph(ShowState, context_schema=ShowContext)
    graph.add_node("moderator_open", make_moderator_open(guest_a, guest_b, moderator))
    graph.add_node(
        "moderator_allocate_floor",
        make_moderator_allocate_floor(guest_a, guest_b, moderator),
    )
    graph.add_node("guest_a", _make_guest_node(guest_a))
    graph.add_node("guest_b", _make_guest_node(guest_b))
    graph.add_node("update_shared_state", make_update_shared_state(guest_a, guest_b))
    graph.add_node("moderator_interject", make_moderator_interject(moderator))
    graph.add_node(
        "moderator_conclude",
        make_moderator_conclude(guest_a, guest_b, moderator),
    )

    graph.add_edge(START, "moderator_open")
    graph.add_edge("moderator_open", "moderator_allocate_floor")
    graph.add_conditional_edges(
        "moderator_allocate_floor",
        make_route_after_allocate(guest_a),
        {"guest_a": "guest_a", "guest_b": "guest_b"},
    )
    graph.add_edge("guest_a", "update_shared_state")
    graph.add_edge("guest_b", "update_shared_state")
    graph.add_conditional_edges(
        "update_shared_state",
        make_route_after_update(moderator, peek_earpiece=peek_earpiece),
        {
            "moderator_allocate_floor": "moderator_allocate_floor",
            "moderator_interject": "moderator_interject",
            "moderator_conclude": "moderator_conclude",
        },
    )
    graph.add_edge("moderator_interject", "moderator_allocate_floor")
    graph.add_edge("moderator_conclude", END)
    return graph.compile()


def run_show(
    topic: str,
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    *,
    max_rounds: int = 3,
    client: Optional[OpenAI] = None,
    enable_web_search: bool = True,
    emit: Optional[EmitCallback] = None,
    poll_earpiece: Optional[EarpiecePoll] = None,
    peek_earpiece: Optional[EarpiecePeek] = None,
    trace_llm_cursor: Optional[Callable[[], int]] = None,
) -> dict[str, Any]:
    """Exécute un show complet et retourne le ShowState final."""
    compiled = build_show_graph(guest_a, guest_b, peek_earpiece=peek_earpiece)
    state = initial_show_state(topic, [guest_a, guest_b], max_rounds)
    context = ShowContext(
        client=client,
        model_internal=SHOW_CONFIG["model_internal"],
        model_delivery=SHOW_CONFIG["model_delivery"],
        enable_web_search=enable_web_search and client is not None,
        emit=emit,
        poll_earpiece=poll_earpiece,
        peek_earpiece=peek_earpiece,
        trace_llm_cursor=trace_llm_cursor,
    )
    return compiled.invoke(
        state,
        context=context,
        config={"recursion_limit": int(SHOW_CONFIG["recursion_limit"])},
    )
