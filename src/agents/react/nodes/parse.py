"""Nœud parse_opponent."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import invoke_internal, notify_step, parse_labeled_lines
from agents.react.prompts.gpt54_system import PARSE_SYSTEM
from agents.react.prompts.onpc_nodes import parse_prompt
from agents.react.state import DebateTurnState
from config.debate_graph import DEBATE_GRAPH_CONFIG


def parse_opponent(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "parse_opponent")
    opponent = state.get("opponent_last") or state.get("topic") or ""
    is_round_one = bool(state.get("is_round_one"))

    if is_round_one:
        return {
            "parsed_claim": opponent,
            "weakness": "cadrage du sujet encore ouvert — imposer votre lecture",
            "current_step": "parse_opponent",
        }

    persona = state.get("persona_vector") or {}
    text = invoke_internal(
        DEBATE_GRAPH_CONFIG["model_internal"],
        PARSE_SYSTEM,
        parse_prompt(opponent, is_round_one),
        temperature=float(persona.get("temperature_facts", 0.4)),
    )
    parsed = parse_labeled_lines(text, ["CLAIM", "WEAKNESS"])
    return {
        "parsed_claim": parsed.get("claim") or opponent,
        "weakness": parsed.get("weakness") or "contradiction non exposée",
        "current_step": "parse_opponent",
    }
