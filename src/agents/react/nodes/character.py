"""Nœud apply_character."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import invoke_internal, notify_step
from agents.react.prompts.gpt54_system import CHARACTER_SYSTEM
from agents.react.prompts.onpc_nodes import character_prompt
from agents.react.state import DebateTurnState
from config.debate_graph import DEBATE_GRAPH_CONFIG


def apply_character(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "apply_character")
    persona = state.get("persona_vector") or {}
    draft = state.get("draft") or ""
    text = invoke_internal(
        DEBATE_GRAPH_CONFIG["model_internal"],
        CHARACTER_SYSTEM,
        character_prompt(draft, persona),
        temperature=float(persona.get("temperature_voice", 1.2)),
        max_tokens=200,
    )
    return {
        "draft": text or draft,
        "current_step": "apply_character",
    }
