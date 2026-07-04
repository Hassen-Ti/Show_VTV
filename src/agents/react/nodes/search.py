"""Nœud search_web."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import notify_step
from agents.react.state import DebateTurnState
from agents.react.tools.search import execute_search_web
from config.debate_graph import DEBATE_GRAPH_CONFIG


def search_web(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "search_web")
    query = (state.get("evidence_query") or "").strip()
    if not query:
        return {"evidence": "", "current_step": "search_web"}

    ctx = runtime.context
    if ctx.search_callback:
        ctx.search_callback(f"🔍 Recherche web : {query[:120]}…")

    model = state.get("delivery_model") or ctx.search_model or DEBATE_GRAPH_CONFIG["model_delivery"]
    evidence = execute_search_web(ctx.client, model, query)
    if evidence.startswith("Erreur"):
        evidence = ""
    return {"evidence": evidence, "current_step": "search_web"}
