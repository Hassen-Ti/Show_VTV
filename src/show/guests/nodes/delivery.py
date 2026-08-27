"""Nœuds de mise en voix : draft → voice → deliver (+ monologue intérieur)."""

from __future__ import annotations

from langgraph.runtime import Runtime

from config.show_config import HIGH_AROUSAL, SHOW_CONFIG
from show import llm, mind as mind_algo
from show.runtime.context import ShowContext, emit_event
from show.guests.nodes import prompts
from show.guests.nodes.factories import NodeFn, _notify
from show.guests.personas.vector import PersonaVector
from show.memory.state import ShowState, TranscriptEntry


def make_draft(persona: PersonaVector) -> NodeFn:
    def draft(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "draft")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.DRAFT_SYSTEM,
            prompts.draft_prompt(persona, mind, state["topic"], state["turn"]),
            temperature=persona.temperature_facts,
            max_tokens=SHOW_CONFIG["internal_max_tokens"],
        )
        fallback = (
            f"Sur {state['topic']}, votre lecture est fragile : {state['turn'].get('weakness', '')}."
        )
        return {"turn": {**state["turn"], "draft": text or fallback}}

    return draft


def make_voice(persona: PersonaVector) -> NodeFn:
    def voice(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "voice")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.VOICE_SYSTEM,
            prompts.voice_prompt(persona, mind, state["topic"], state["turn"].get("draft", "")),
            temperature=mind_algo.effective_voice_temperature(mind, persona),
            max_tokens=SHOW_CONFIG["internal_max_tokens"],
        )
        return {"turn": {**state["turn"], "voiced": text or state["turn"].get("draft", "")}}

    return voice


def make_deliver(persona: PersonaVector) -> NodeFn:
    def deliver(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "deliver")
        ctx = runtime.context
        mind = state["minds"][persona.agent_id]
        turn = state["turn"]
        sentence_max = mind_algo.effective_sentence_max(mind, persona, HIGH_AROUSAL)

        final = llm.think(
            ctx.model_delivery or SHOW_CONFIG["model_delivery"],
            prompts.DELIVER_SYSTEM,
            prompts.deliver_prompt(turn.get("voiced", turn.get("draft", "")), sentence_max),
            temperature=mind_algo.effective_voice_temperature(mind, persona),
            max_tokens=SHOW_CONFIG["delivery_max_tokens"],
        ) or turn.get("voiced") or turn.get("draft") or ""

        monologue = llm.think(
            ctx.model_internal or SHOW_CONFIG["model_internal"],
            prompts.MONOLOGUE_SYSTEM,
            prompts.monologue_prompt(persona, mind, state["topic"], final),
            temperature=persona.temperature_voice,
        )

        # Avoir répondu renforce la conviction et solde une rancune.
        mind = mind_algo.update_conviction(mind, turn.get("persuasion", 0.0), countered=True)
        mind = dict(mind)  # type: ignore[assignment]
        mind["inner_monologue"] = monologue
        if mind["grudges"]:
            mind["grudges"] = mind["grudges"][1:]

        entry = TranscriptEntry(
            round=state["round"],
            speaker=persona.agent_id,
            speaker_name=persona.name,
            role="guest",
            text=final,
            tactic=turn.get("tactic", ""),
            evidence_used=bool(turn.get("evidence")),
        )
        emit_event(
            ctx,
            {
                "type": "turn",
                "agent": persona.agent_id,
                "name": persona.name,
                "round": state["round"],
                "text": final,
                "tactic": entry["tactic"],
                "evidence_used": entry["evidence_used"],
            },
        )
        emit_event(
            ctx,
            {"type": "inner_monologue", "agent": persona.agent_id, "text": monologue},
        )
        return {
            "transcript": [entry],
            "minds": {**state["minds"], persona.agent_id: mind},
            "turn": {**turn, "final": final},
        }

    return deliver
