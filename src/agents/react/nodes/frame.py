"""Nœud choose_frame."""

from __future__ import annotations

from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from agents.react.nodes.common import invoke_internal, notify_step, parse_labeled_lines, parse_yes_no
from agents.react.prompts.gpt54_system import FRAME_SYSTEM
from agents.react.prompts.onpc_nodes import frame_prompt
from agents.react.state import DebateTurnState
from config.debate_graph import DEBATE_GRAPH_CONFIG


def choose_frame(
    state: DebateTurnState,
    runtime: Runtime[DebateGraphContext],
) -> dict:
    notify_step(runtime, "choose_frame")
    persona = state.get("persona_vector") or {}
    text = invoke_internal(
        DEBATE_GRAPH_CONFIG["model_internal"],
        FRAME_SYSTEM,
        frame_prompt(
            state.get("parsed_claim") or "",
            state.get("weakness") or "",
            state.get("topic") or "",
            str(persona.get("rhetoric", "journalist")),
        ),
        temperature=float(persona.get("temperature_facts", 0.4)),
    )
    parsed = parse_labeled_lines(text, ["FRAME", "NEEDS_EVIDENCE", "EVIDENCE_QUERY"])
    needs = parse_yes_no(parsed.get("needs_evidence", ""))
    if persona.get("rhetoric") == "journalist" and not needs and not state.get("is_round_one"):
        needs = True
    return {
        "frame": parsed.get("frame") or "contre-attaque directe",
        "needs_evidence": needs,
        "evidence_query": parsed.get("evidence_query") or "",
        "current_step": "choose_frame",
    }
