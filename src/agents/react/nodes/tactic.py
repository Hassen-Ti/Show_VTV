"""Nœud select_tactic."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import (
    first_allowed_tactic,
    invoke_internal,
    notify_step,
    parse_labeled_lines,
)
from agents.react.prompts.gpt54_system import TACTIC_SYSTEM
from agents.react.prompts.onpc_nodes import tactic_prompt
from agents.react.state import DebateTurnState
from config.debate_graph import DEBATE_GRAPH_CONFIG


def select_tactic(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "select_tactic")
    persona = state.get("persona_vector") or {}
    allowed = list(persona.get("tactics") or ["clash"])
    fallback = "pivot" if state.get("is_round_one") else allowed[0]

    text = invoke_internal(
        DEBATE_GRAPH_CONFIG["model_internal"],
        TACTIC_SYSTEM,
        tactic_prompt(
            state.get("frame") or "",
            allowed,
            str(persona.get("affective", "triumphant")),
            bool(state.get("is_round_one")),
        ),
        temperature=float(persona.get("temperature_facts", 0.4)),
    )
    parsed = parse_labeled_lines(text, ["TACTIC"])
    tactic = first_allowed_tactic(parsed.get("tactic", ""), allowed, fallback)
    return {"tactic": tactic, "current_step": "select_tactic"}
