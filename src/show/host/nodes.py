"""Nœuds LangGraph de l'animateur (open / floor / interject / conclude).

Interjection policy (evaluated only when a round is complete — both guests spoke):

1. **Conclude** — ``round >= max_rounds`` always wins (show must end even if
   an earpiece packet is still queued).
2. **Earpiece** — spectator packet pending (``peek_earpiece``) → interject to
   read it on air. Takes precedence over tension / cadence so the audience
   injection is not starved by heat checks.
3. **Tension / cadence** — ``tension > interject_threshold`` (SYSLOAD spike)
   **or** even round beat (``round % 2 == 0``) → interject to cool or relaunch.
4. Otherwise → ``moderator_allocate_floor``.
"""

from __future__ import annotations

from typing import Optional

from langgraph.runtime import Runtime

from config.show_config import SHOW_CONFIG
from show import llm
from show.guests.personas.vector import PersonaVector
from show.host.persona import ModeratorPersona
from show.host.prompts import MODERATOR_SYSTEM
from show.memory.state import ShowState, TranscriptEntry
from show.runtime.context import (
    EarpiecePeek,
    ShowContext,
    drain_earpiece,
    emit_event,
)


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


def _moderator_say(
    context: ShowContext,
    moderator: ModeratorPersona,
    instruction: str,
    *,
    sentence_max: Optional[int] = None,
) -> str:
    limit = moderator.sentence_max if sentence_max is None else sentence_max
    return llm.think(
        context.model_internal or SHOW_CONFIG["model_internal"],
        MODERATOR_SYSTEM,
        (
            f"<identity>Tu es {moderator.name}, {moderator.style}.</identity>\n"
            f"<length_limit>Maximum {limit} phrases (hard cap)</length_limit>\n"
            f"<instruction>{instruction}</instruction>"
        ),
        temperature=moderator.temperature,
    )


def make_moderator_open(
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    moderator: ModeratorPersona,
):
    def moderator_open(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        audience = drain_earpiece(runtime.context)
        audience_clause = ""
        if audience:
            audience_clause = (
                f" Avant de commencer, un téléspectateur nous écrit : « {audience} ». "
                "Mentionne-le brièvement à l'antenne et promets d'y revenir pendant le débat."
            )
            emit_event(
                runtime.context,
                {"type": "earpiece", "phase": "opening", "text": audience},
            )
        text = _moderator_say(
            runtime.context,
            moderator,
            f"Ouvre le débat sur « {state['topic']} ». Présente les deux invités : "
            f"{guest_a.name} ({guest_a.domain}, spécialiste de {guest_a.specialization}) et "
            f"{guest_b.name} ({guest_b.domain}, spécialiste de {guest_b.specialization}). "
            "Pose l'enjeu, crée l'attente."
            + audience_clause,
            sentence_max=moderator.sentence_max,
        )
        entry = _moderator_entry({**state, "round": 0}, text, moderator)
        emit_event(runtime.context, {"type": "moderator", "round": 0, "text": text})
        return {"transcript": [entry], "round": 1}

    return moderator_open


def make_moderator_allocate_floor(
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    moderator: ModeratorPersona,
):
    guests = (guest_a, guest_b)

    def moderator_allocate_floor(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        turn_index = state["turn_index"] + 1
        round_num = (turn_index + 1) // 2
        speaker = guests[(turn_index - 1) % 2]
        text = _moderator_say(
            runtime.context,
            moderator,
            f"Round {round_num} : donne la parole à {speaker.name} "
            f"({speaker.domain}). Une seule phrase de passage de parole, incisive.",
            sentence_max=1,
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

    return moderator_allocate_floor


def make_route_after_allocate(guest_a: PersonaVector):
    def route_after_allocate(state: ShowState) -> str:
        return decide_allocate_route(state["current_speaker"], guest_a.agent_id)

    return route_after_allocate


def decide_allocate_route(current_speaker: str, guest_a_id: str) -> str:
    """Pure helper: map ``current_speaker`` to guest subgraph node name."""
    return "guest_a" if current_speaker == guest_a_id else "guest_b"


def decide_moderator_route(
    *,
    turn_index: int,
    round_num: int,
    max_rounds: int,
    tension: float,
    interject_threshold: float,
    earpiece_pending: bool,
) -> str:
    """Pure routing policy after ``update_shared_state`` (see module docstring)."""
    round_complete = turn_index % 2 == 0
    if not round_complete:
        return "moderator_allocate_floor"
    if round_num >= max_rounds:
        return "moderator_conclude"
    # Earpiece before tension: audience packets must not wait on heat cadence.
    if earpiece_pending:
        return "moderator_interject"
    if tension > interject_threshold or round_num % 2 == 0:
        return "moderator_interject"
    return "moderator_allocate_floor"


def make_route_after_update(
    moderator: ModeratorPersona,
    *,
    peek_earpiece: Optional[EarpiecePeek] = None,
):
    def route_after_update(state: ShowState) -> str:
        earpiece_pending = bool(peek_earpiece and peek_earpiece())
        return decide_moderator_route(
            turn_index=state["turn_index"],
            round_num=state["round"],
            max_rounds=state["max_rounds"],
            tension=state["tension"],
            interject_threshold=moderator.interject_threshold,
            earpiece_pending=earpiece_pending,
        )

    return route_after_update


def make_moderator_interject(moderator: ModeratorPersona):
    def moderator_interject(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        audience = drain_earpiece(runtime.context)
        pending_audience = ""
        if audience:
            # Earpiece path: always drain + surface on air, regardless of tension.
            pending_audience = audience
            emit_event(
                runtime.context,
                {"type": "earpiece", "phase": "live", "text": audience},
            )
            text = _moderator_say(
                runtime.context,
                moderator,
                f"Un message nous parvient du public : « {audience} ». "
                "Lis-le à l'antenne avec tes mots, reformule-le clairement, "
                "puis relance le débat en demandant aux invités d'y répondre.",
                sentence_max=moderator.sentence_max,
            )
        else:
            # Tension / cadence path: cool high SYSLOAD or point the real disagreement.
            last_guests = [e for e in state["transcript"] if e["role"] == "guest"][-2:]
            exchange = "\n".join(f"{e['speaker_name']}: {e['text']}" for e in last_guests)
            heat = (
                "Le ton monte, calme le jeu sans éteindre le débat."
                if state["tension"] > moderator.interject_threshold
                else "Relance le débat en pointant le vrai désaccord."
            )
            text = _moderator_say(
                runtime.context,
                moderator,
                f"Dernier échange :\n{exchange}\nTension du plateau : {state['tension']:.2f}. {heat}",
                sentence_max=moderator.sentence_max,
            )
        entry = _moderator_entry(state, text, moderator)
        emit_event(
            runtime.context, {"type": "moderator", "round": state["round"], "text": text}
        )
        return {
            "transcript": [entry],
            "moderator_notes": [f"interjection round {state['round']}"],
            "pending_audience_question": pending_audience,
        }

    return moderator_interject


def make_moderator_conclude(
    guest_a: PersonaVector,
    guest_b: PersonaVector,
    moderator: ModeratorPersona,
):
    guests = (guest_a, guest_b)

    def moderator_conclude(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        drift_lines = []
        for guest in guests:
            history = state["stance_history"][guest.agent_id]
            drift_lines.append(
                f"{guest.name} : position {history[0]:+.2f} → {history[-1]:+.2f}"
            )
        # Conclusion may need one extra sentence for the signature line.
        conclude_limit = max(moderator.sentence_max, 3)
        text = _moderator_say(
            runtime.context,
            moderator,
            "Conclus le débat. Évolution réelle des positions :\n"
            + "\n".join(drift_lines)
            + f"\nDis honnêtement qui a bougé, puis signe : « {moderator.signature} »",
            sentence_max=conclude_limit,
        )
        entry = _moderator_entry(state, text, moderator)
        emit_event(
            runtime.context, {"type": "moderator", "round": state["round"], "text": text}
        )
        return {"transcript": [entry]}

    return moderator_conclude
