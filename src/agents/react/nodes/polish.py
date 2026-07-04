"""Nœud polish_onpc."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import invoke_internal, notify_step
from agents.react.prompts.gpt54_system import POLISH_SYSTEM
from agents.react.prompts.onpc_nodes import polish_prompt
from agents.react.state import DebateTurnState
from config.debate_graph import DEBATE_GRAPH_CONFIG


def polish_onpc(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "polish_onpc")
    persona = state.get("persona_vector") or {}
    draft = state.get("draft") or ""
    delivery_model = state.get("delivery_model") or DEBATE_GRAPH_CONFIG["model_delivery"]
    max_tokens = int(
        state.get("delivery_max_tokens") or DEBATE_GRAPH_CONFIG.get("delivery_max_tokens", 200)
    )
    text = invoke_internal(
        delivery_model,
        POLISH_SYSTEM,
        polish_prompt(draft, int(persona.get("sentence_max", 2))),
        temperature=float(persona.get("temperature_voice", 1.2)),
        max_tokens=max_tokens,
    )
    return {
        "final": text or draft,
        "current_step": "polish_onpc",
    }
