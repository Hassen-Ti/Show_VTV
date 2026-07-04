"""Arêtes conditionnelles du graphe débatteur ONPC."""

from __future__ import annotations

from config.debate_graph import DEBATE_GRAPH_CONFIG
from agents.react.state import DebateTurnState


def route_after_frame(state: DebateTurnState) -> str:
    """Route LangGraph après ``choose_frame`` (doc: conditional edges)."""
    if not state.get("enable_web_search", True):
        return "select_tactic"
    if state.get("is_round_one") and DEBATE_GRAPH_CONFIG.get("skip_search_round_1"):
        return "select_tactic"
    if state.get("needs_evidence") and (state.get("evidence_query") or "").strip():
        return "search_web"
    return "select_tactic"
