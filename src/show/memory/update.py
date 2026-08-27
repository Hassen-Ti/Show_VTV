"""Nœud moteur ``update_shared_state`` : tension, stance_history, décroissance.

Write-contract moteur (voir aussi ``state`` module docstring) :
- recalcule ``tension`` via ``mind.compute_tension`` (minds + entrées du round) ;
- étend ``stance_history`` d'un point par agent encore présent dans ``minds`` ;
- applique ``mind.decay`` à chaque invité connu **si** le round est complet
  (``turn_index % 2 == 0``).

Tolérant aux absences : invité sans entrée dans ``minds``, ``stance_history``
vide, ``transcript`` manquant — pas d'exception, pas de clé inventée.
"""

from __future__ import annotations

from langgraph.runtime import Runtime

from show.guests.personas.vector import PersonaVector
from show.memory import mind as mind_algo
from show.memory.state import ShowState
from show.runtime.context import ShowContext, emit_event


def make_update_shared_state(guest_a: PersonaVector, guest_b: PersonaVector):
    guests = (guest_a, guest_b)

    def update_shared_state(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        minds = dict(state.get("minds") or {})
        current_round = state.get("round", 0)
        transcript = state.get("transcript") or []
        round_entries = [e for e in transcript if e.get("round") == current_round]
        round_complete = int(state.get("turn_index", 0)) % 2 == 0
        if round_complete:
            for guest in guests:
                current = minds.get(guest.agent_id)
                if current is not None:
                    minds[guest.agent_id] = mind_algo.decay(current, guest)

        tension = mind_algo.compute_tension(minds, round_entries)
        prior_history = state.get("stance_history") or {}
        stance_history = {
            agent_id: list(history) + [minds[agent_id]["stance"]]
            for agent_id, history in prior_history.items()
            if agent_id in minds
        }
        # Agents présents dans minds mais absents de l'historique → seed d'une série.
        for agent_id, mind in minds.items():
            if agent_id not in stance_history:
                stance_history[agent_id] = [mind["stance"]]

        emit_event(
            runtime.context,
            {
                "type": "stance_update",
                "round": current_round,
                "tension": tension,
                "stances": {aid: minds[aid]["stance"] for aid in minds},
                "convictions": {aid: minds[aid]["conviction"] for aid in minds},
            },
        )
        return {"minds": minds, "tension": tension, "stance_history": stance_history}

    return update_shared_state
