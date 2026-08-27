"""Nœud moteur ``update_shared_state`` : tension, stance_history, décroissance."""

from __future__ import annotations

from langgraph.runtime import Runtime

from show.guests.personas.vector import PersonaVector
from show.memory import mind as mind_algo
from show.memory.state import ShowState
from show.runtime.context import ShowContext, emit_event


def make_update_shared_state(guest_a: PersonaVector, guest_b: PersonaVector):
    guests = (guest_a, guest_b)

    def update_shared_state(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        minds = dict(state["minds"])
        round_entries = [
            e for e in state["transcript"] if e["round"] == state["round"]
        ]
        round_complete = state["turn_index"] % 2 == 0
        if round_complete:
            for guest in guests:
                minds[guest.agent_id] = mind_algo.decay(minds[guest.agent_id], guest)

        tension = mind_algo.compute_tension(minds, round_entries)
        stance_history = {
            agent_id: history + [minds[agent_id]["stance"]]
            for agent_id, history in state["stance_history"].items()
        }
        emit_event(
            runtime.context,
            {
                "type": "stance_update",
                "round": state["round"],
                "tension": tension,
                "stances": {aid: minds[aid]["stance"] for aid in minds},
                "convictions": {aid: minds[aid]["conviction"] for aid in minds},
            },
        )
        return {"minds": minds, "tension": tension, "stance_history": stance_history}

    return update_shared_state
