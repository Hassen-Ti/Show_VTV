"""Orchestrateur du show : modérateur + 2 sous-graphes invités sur un état partagé.

Topologie :
    START → moderator_open → moderator_allocate_floor
        → (guest_a | guest_b) → update_shared_state
        → (moderator_allocate_floor | moderator_interject | moderator_conclude)
"""

from __future__ import annotations

from typing import Any, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from openai import OpenAI

from config.show_config import SHOW_CONFIG
from show import llm, mind as mind_algo
from show.context import EmitCallback, ShowContext, emit_event
from show.graph.guest_subgraph import build_guest_subgraph
from show.nodes import prompts
from show.personas.registry import MODERATOR_PERSONA, ModeratorPersona
from show.personas.vector import PersonaVector
from show.state import ShowState, TranscriptEntry, initial_show_state


def _moderator_entry(state: ShowState, text: str, moderator: ModeratorPersona) -> TranscriptEntry:
    return TranscriptEntry(
        round=state.get("round", 0),
        speaker=moderator.agent_id,
        speaker_name=moderator.name,
        role="moderator",
        text=text,
        tactic="",
        evidence_used=False,
    )


def _moderator_say(context: ShowContext, moderator: ModeratorPersona, instruction: str) -> str:
    return llm.think(
        context.model_internal or SHOW_CONFIG["model_internal"],
        prompts.MODERATOR_SYSTEM,
        (
            f"<identity>Tu es {moderator.name}, {moderator.style}.</identity>\n"
            f"<length_limit>Maximum {moderator.sentence_max} phrases</length_limit>\n"
            f"<instruction>{instruction}</instruction>"
        ),
        temperature=moderator.temperature,
    )


def _make_guest_node(persona: PersonaVector):
    """Enveloppe le sous-graphe invité pour ne renvoyer que le delta d'état.

    Le transcript porte un reducer ``operator.add`` : renvoyer l'état final du
    sous-graphe tel quel ré-appendrait les entrées héritées du parent.
    """
    compiled = build_guest_subgraph(persona)

    def guest_node(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        inherited = len(state["transcript"])
        out = compiled.invoke(state, context=runtime.context)
        return {
            "transcript": out["transcript"][inherited:],
            "minds": out["minds"],
            "turn": out["turn"],
        }

    return guest_node


def build_show_graph(
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    moderator: ModeratorPersona = MODERATOR_PERSONA,
):
    guests = (guest_a, guest_b)

    def moderator_open(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        text = _moderator_say(
            runtime.context,
            moderator,
            f"Ouvre le débat sur « {state['topic']} ». Présente les deux invités : "
            f"{guest_a.name} ({guest_a.domain}, spécialiste de {guest_a.specialization}) et "
            f"{guest_b.name} ({guest_b.domain}, spécialiste de {guest_b.specialization}). "
            "Pose l'enjeu, crée l'attente.",
        )
        entry = _moderator_entry({**state, "round": 0}, text, moderator)
        emit_event(runtime.context, {"type": "moderator", "round": 0, "text": text})
        return {"transcript": [entry], "round": 1}

    def moderator_allocate_floor(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        turn_index = state["turn_index"] + 1
        round_num = (turn_index + 1) // 2
        speaker = guests[(turn_index - 1) % 2]
        text = _moderator_say(
            runtime.context,
            moderator,
            f"Round {round_num} : donne la parole à {speaker.name} "
            f"({speaker.domain}). Une seule phrase de passage de parole, incisive.",
        )
        entry = _moderator_entry({**state, "round": round_num}, text, moderator)
        emit_event(runtime.context, {"type": "moderator", "round": round_num, "text": text})
        return {
            "transcript": [entry],
            "turn_index": turn_index,
            "round": round_num,
            "current_speaker": speaker.agent_id,
            "turn": {},
        }

    def route_after_allocate(state: ShowState) -> str:
        return "guest_a" if state["current_speaker"] == guest_a.agent_id else "guest_b"

    def update_shared_state(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        """Nœud moteur (pas un agent) : tension, historique des stances, décroissance."""
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

    def route_after_update(state: ShowState) -> str:
        round_complete = state["turn_index"] % 2 == 0
        if round_complete and state["round"] >= state["max_rounds"]:
            return "moderator_conclude"
        if round_complete and (
            state["tension"] > moderator.interject_threshold or state["round"] % 2 == 0
        ):
            return "moderator_interject"
        return "moderator_allocate_floor"

    def moderator_interject(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        last_guests = [e for e in state["transcript"] if e["role"] == "guest"][-2:]
        exchange = "\n".join(f"{e['speaker_name']}: {e['text']}" for e in last_guests)
        heat = "Le ton monte, calme le jeu sans éteindre le débat." if state[
            "tension"
        ] > moderator.interject_threshold else "Relance le débat en pointant le vrai désaccord."
        text = _moderator_say(
            runtime.context,
            moderator,
            f"Dernier échange :\n{exchange}\nTension du plateau : {state['tension']:.2f}. {heat}",
        )
        entry = _moderator_entry(state, text, moderator)
        emit_event(
            runtime.context, {"type": "moderator", "round": state["round"], "text": text}
        )
        return {"transcript": [entry], "moderator_notes": [f"interjection round {state['round']}"]}

    def moderator_conclude(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        drift_lines = []
        for guest in guests:
            history = state["stance_history"][guest.agent_id]
            drift_lines.append(
                f"{guest.name} : position {history[0]:+.2f} → {history[-1]:+.2f}"
            )
        text = _moderator_say(
            runtime.context,
            moderator,
            "Conclus le débat. Évolution réelle des positions :\n"
            + "\n".join(drift_lines)
            + f"\nDis honnêtement qui a bougé, puis signe : « {moderator.signature} »",
        )
        entry = _moderator_entry(state, text, moderator)
        emit_event(
            runtime.context, {"type": "moderator", "round": state["round"], "text": text}
        )
        return {"transcript": [entry]}

    graph = StateGraph(ShowState, context_schema=ShowContext)
    graph.add_node("moderator_open", moderator_open)
    graph.add_node("moderator_allocate_floor", moderator_allocate_floor)
    graph.add_node("guest_a", _make_guest_node(guest_a))
    graph.add_node("guest_b", _make_guest_node(guest_b))
    graph.add_node("update_shared_state", update_shared_state)
    graph.add_node("moderator_interject", moderator_interject)
    graph.add_node("moderator_conclude", moderator_conclude)

    graph.add_edge(START, "moderator_open")
    graph.add_edge("moderator_open", "moderator_allocate_floor")
    graph.add_conditional_edges(
        "moderator_allocate_floor",
        route_after_allocate,
        {"guest_a": "guest_a", "guest_b": "guest_b"},
    )
    graph.add_edge("guest_a", "update_shared_state")
    graph.add_edge("guest_b", "update_shared_state")
    graph.add_conditional_edges(
        "update_shared_state",
        route_after_update,
        {
            "moderator_allocate_floor": "moderator_allocate_floor",
            "moderator_interject": "moderator_interject",
            "moderator_conclude": "moderator_conclude",
        },
    )
    graph.add_edge("moderator_interject", "moderator_allocate_floor")
    graph.add_edge("moderator_conclude", END)
    return graph.compile()


def run_show(
    topic: str,
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    *,
    max_rounds: int = 3,
    client: Optional[OpenAI] = None,
    enable_web_search: bool = True,
    emit: Optional[EmitCallback] = None,
) -> dict[str, Any]:
    """Exécute un show complet et retourne le ShowState final."""
    compiled = build_show_graph(guest_a, guest_b)
    state = initial_show_state(topic, [guest_a, guest_b], max_rounds)
    context = ShowContext(
        client=client,
        model_internal=SHOW_CONFIG["model_internal"],
        model_delivery=SHOW_CONFIG["model_delivery"],
        enable_web_search=enable_web_search and client is not None,
        emit=emit,
    )
    return compiled.invoke(
        state,
        context=context,
        config={"recursion_limit": int(SHOW_CONFIG["recursion_limit"])},
    )
