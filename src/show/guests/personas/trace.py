"""Enregistrement des traces agent : état I/O par nœud."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from langgraph.runtime import Runtime

from show.guests.nodes import STEP_LABELS
from show.memory.state import ShowState
from show.runtime.context import ShowContext, emit_event

if TYPE_CHECKING:
    from show.guests.nodes.factories import NodeFn
    from show.guests.personas.vector import PersonaVector


def mind_snapshot(mind: dict[str, Any]) -> dict[str, Any]:
    return {
        "stance": mind.get("stance"),
        "conviction": mind.get("conviction"),
        "valence": mind.get("valence"),
        "arousal": mind.get("arousal"),
        "beliefs": list(mind.get("beliefs", [])),
        "grudges": list(mind.get("grudges", [])),
        "inner_monologue": mind.get("inner_monologue", ""),
    }


def make_traced_node(persona: PersonaVector, step: str, inner: NodeFn) -> NodeFn:
    """Enveloppe un nœud invité pour émettre l'état I/O complet."""

    def node(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        agent_id = persona.agent_id
        turn_in = dict(state.get("turn") or {})
        mind_in = mind_snapshot(state["minds"][agent_id])
        show_in = {
            "topic": state.get("topic", ""),
            "round": state.get("round", 0),
            "tension": round(float(state.get("tension", 0.0)), 4),
            "turn_index": state.get("turn_index", 0),
        }
        cursor_fn = runtime.context.trace_llm_cursor
        llm_from = cursor_fn() if cursor_fn else 0

        result = inner(state, runtime)

        llm_to = cursor_fn() if cursor_fn else llm_from
        output: dict[str, Any] = {}
        if "turn" in result:
            output["turn"] = result["turn"]
        if "minds" in result and agent_id in result["minds"]:
            output["mind"] = mind_snapshot(result["minds"][agent_id])
        if "transcript" in result:
            output["transcript"] = list(result["transcript"])

        emit_event(
            runtime.context,
            {
                "type": "step_io",
                "agent": agent_id,
                "agent_name": persona.name,
                "step": step,
                "label": STEP_LABELS.get(step, step),
                "llm_from": llm_from,
                "llm_to": llm_to,
                "input": {"turn": turn_in, "mind": mind_in, "show": show_in},
                "output": output,
            },
        )
        return result

    return node
