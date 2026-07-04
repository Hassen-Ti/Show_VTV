"""Nœud draft_argument."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import invoke_internal, notify_step
from agents.react.prompts.gpt54_system import DRAFT_SYSTEM
from agents.react.prompts.onpc_nodes import draft_prompt
from agents.react.state import DebateTurnState
from config.debate_graph import DEBATE_GRAPH_CONFIG


def draft_argument(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "draft_argument")
    persona = state.get("persona_vector") or {}
    text = invoke_internal(
        DEBATE_GRAPH_CONFIG["model_internal"],
        DRAFT_SYSTEM,
        draft_prompt(
            state.get("frame") or "",
            state.get("tactic") or "clash",
            state.get("parsed_claim") or "",
            state.get("weakness") or "",
            state.get("evidence") or "",
            state.get("system_prompt_legacy") or "",
            state.get("debate_history") or "",
        ),
        temperature=float(persona.get("temperature_facts", 0.4)),
        max_tokens=200,
    )
    draft = text or (
        f"Sur {state.get('topic', 'ce sujet')}, votre angle est fragile face à {state.get('frame', 'nos arguments')}."
    )
    return {"draft": draft, "current_step": "draft_argument"}
