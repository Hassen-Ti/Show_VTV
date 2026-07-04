"""Assemblage LangGraph du pipeline débatteur ONPC.

Patterns officiels LangGraph (https://github.com/langchain-ai/langgraph) :
- ``StateGraph(state_schema, context_schema=...)``
- nœuds ``(state, runtime: Runtime[Context]) -> partial state``
- ``invoke(state, context=..., config={"recursion_limit": n})``
- arêtes conditionnelles via ``add_conditional_edges``
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable, Optional

from langgraph.graph import END, START, StateGraph
from openai import OpenAI

from agents.react.context import DebateGraphContext
from agents.react.nodes.character import apply_character
from agents.react.nodes.draft import draft_argument
from agents.react.nodes.frame import choose_frame
from agents.react.nodes.parse import parse_opponent
from agents.react.nodes.polish import polish_onpc
from agents.react.nodes.search import search_web
from agents.react.nodes.tactic import select_tactic
from agents.react.routing import route_after_frame
from agents.react.state import DebateTurnState, initial_state
from config.debate_graph import DEBATE_GRAPH_CONFIG


def build_debate_graph():
    """Construit et compile le graphe (équivalent ``builder.compile()`` doc LangGraph)."""
    graph = StateGraph(DebateTurnState, context_schema=DebateGraphContext)
    graph.add_node("parse_opponent", parse_opponent)
    graph.add_node("choose_frame", choose_frame)
    graph.add_node("search_web", search_web)
    graph.add_node("select_tactic", select_tactic)
    graph.add_node("draft_argument", draft_argument)
    graph.add_node("apply_character", apply_character)
    graph.add_node("polish_onpc", polish_onpc)
    graph.add_edge(START, "parse_opponent")
    graph.add_edge("parse_opponent", "choose_frame")
    graph.add_conditional_edges(
        "choose_frame",
        route_after_frame,
        {"search_web": "search_web", "select_tactic": "select_tactic"},
    )
    graph.add_edge("search_web", "select_tactic")
    graph.add_edge("select_tactic", "draft_argument")
    graph.add_edge("draft_argument", "apply_character")
    graph.add_edge("apply_character", "polish_onpc")
    graph.add_edge("polish_onpc", END)
    return graph.compile()


@lru_cache(maxsize=1)
def get_compiled_debate_graph():
    return build_debate_graph()


def draw_debate_graph_mermaid(*, xray: bool = True) -> str:
    """Diagramme Mermaid (``compiled.get_graph().draw_mermaid()``)."""
    return get_compiled_debate_graph().get_graph(xray=xray).draw_mermaid()


def run_debate_turn(
    client: OpenAI,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str,
    user_input: str,
    persona_vector: dict,
    enable_web_search: bool = True,
    stream_callback: Optional[Callable[[str], None]] = None,
    search_callback: Optional[Callable[[str], None]] = None,
    step_callback: Optional[Callable[[str], None]] = None,
    topic: str = "",
) -> str:
    _ = temperature
    delivery_model = model or DEBATE_GRAPH_CONFIG["model_delivery"]
    state = initial_state(
        user_input,
        topic=topic,
        persona_vector=persona_vector,
        system_prompt_legacy=system_prompt,
        enable_web_search=enable_web_search,
        delivery_model=delivery_model,
        delivery_max_tokens=max_tokens,
    )
    context = DebateGraphContext(
        client=client,
        search_model=delivery_model,
        step_callback=step_callback,
        search_callback=search_callback,
    )
    limit = int(DEBATE_GRAPH_CONFIG.get("recursion_limit", 12))
    try:
        result = get_compiled_debate_graph().invoke(
            state,
            context=context,
            config={"recursion_limit": limit},
        )
    except Exception as e:
        return f"Error: {e}"

    final = (result.get("final") or "").strip()
    if not final:
        return "Error: réponse vide après exécution du graphe débatteur."

    if stream_callback:
        from agents.react.executor import _simulate_stream

        _simulate_stream(final, stream_callback)
    return final
