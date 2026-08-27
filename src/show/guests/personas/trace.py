"""Enregistrement des traces agent : état, I/O par nœud, appels LLM."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, TYPE_CHECKING

from langgraph.runtime import Runtime

from show.runtime.context import ShowContext, emit_event
from show.guests.nodes import STEP_LABELS
from show.memory.state import ShowState

if TYPE_CHECKING:
    from show.guests.nodes.factories import NodeFn
    from show.guests.personas.vector import PersonaVector


def _phase_from_system(system: str) -> str:
    markers = (
        ("SCORE", "listen"),
        ("Planifie", "plan"),
        ("Critique le brouillon", "reflect"),
        ("VERDICT", "critic_verify"),
        ("Corrige le brouillon", "self_correct"),
        ("TACTIC", "strategize"),
        ("monologue intérieur", "inner_monologue"),
        ("brouillon interne", "draft"),
        ("Applique la voix", "voice"),
        ("réplique finale", "deliver"),
        ("concession partielle", "concede"),
        ("raisonnement interne", "think"),
        ("Animateur", "moderator"),
    )
    for token, phase in markers:
        if token in system:
            return phase
    return "llm"


@dataclass
class LlmCallRecord:
    phase: str
    system: str
    user: str
    response: str


@dataclass
class StepIO:
    """Une étape du graphe : état entrant, appels LLM, delta sortant."""

    index: int
    agent: str
    agent_name: str
    step: str
    label: str
    input_turn: dict[str, Any]
    input_mind: dict[str, Any]
    input_show: dict[str, Any]
    output: dict[str, Any]
    llm_calls: list[LlmCallRecord] = field(default_factory=list)


@dataclass
class ArchitectureTrace:
    architecture_id: str
    architecture_name: str
    source: str
    reference: str
    cognitive_sequence: str
    persona_name: str
    personality: str
    domain: str
    topic: str
    quality_score: float
    rank: int = 0
    agents: list[dict[str, str]] = field(default_factory=list)
    pipeline: list[StepIO] = field(default_factory=list)
    show_initial: dict[str, Any] = field(default_factory=dict)
    show_final: dict[str, Any] = field(default_factory=dict)
    llm_calls: list[LlmCallRecord] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    on_air_response: str = ""
    inner_monologue: str = ""
    tactic_used: str = ""
    evidence_used: bool = False
    tension_final: float = 0.0


class TraceRecorder:
    """Enveloppe ``llm.think``, collecte événements et curseur LLM."""

    def __init__(self, inner: Callable[..., str]):
        self._inner = inner
        self.llm_calls: list[LlmCallRecord] = []
        self.events: list[dict[str, Any]] = []

    def llm_cursor(self) -> int:
        return len(self.llm_calls)

    def think(self, model, system, user, *, temperature, max_tokens=None) -> str:
        response = self._inner(model, system, user, temperature=temperature, max_tokens=max_tokens)
        self.llm_calls.append(
            LlmCallRecord(
                phase=_phase_from_system(system),
                system=system or "",
                user=user or "",
                response=response,
            )
        )
        return response

    def emit(self, event: dict[str, Any]) -> None:
        self.events.append(event)

    def trace_context_hooks(self) -> dict[str, Any]:
        return {"trace_llm_cursor": self.llm_cursor}


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


def build_pipeline(events: list[dict[str, Any]], llm_calls: list[LlmCallRecord]) -> list[StepIO]:
    pipeline: list[StepIO] = []
    for ev in events:
        if ev.get("type") != "step_io":
            continue
        start = int(ev.get("llm_from", 0))
        end = int(ev.get("llm_to", start))
        inp = ev.get("input") or {}
        pipeline.append(
            StepIO(
                index=len(pipeline) + 1,
                agent=ev["agent"],
                agent_name=ev.get("agent_name", ev["agent"]),
                step=ev["step"],
                label=ev.get("label", ev["step"]),
                input_turn=dict(inp.get("turn") or {}),
                input_mind=dict(inp.get("mind") or {}),
                input_show=dict(inp.get("show") or {}),
                output=dict(ev.get("output") or {}),
                llm_calls=list(llm_calls[start:end]),
            )
        )
    return pipeline


def show_state_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    minds = {
        aid: mind_snapshot(m) for aid, m in (state.get("minds") or {}).items()
    }
    transcript = [
        {
            "round": e.get("round"),
            "speaker": e.get("speaker"),
            "speaker_name": e.get("speaker_name"),
            "role": e.get("role"),
            "text": e.get("text"),
            "tactic": e.get("tactic"),
            "evidence_used": e.get("evidence_used"),
        }
        for e in (state.get("transcript") or [])
    ]
    return {
        "topic": state.get("topic", ""),
        "round": state.get("round", 0),
        "max_rounds": state.get("max_rounds", 0),
        "turn_index": state.get("turn_index", 0),
        "tension": round(float(state.get("tension", 0.0)), 4),
        "current_speaker": state.get("current_speaker", ""),
        "turn": dict(state.get("turn") or {}),
        "minds": minds,
        "stance_history": dict(state.get("stance_history") or {}),
        "transcript": transcript,
    }


def turn_outputs_from_state(turn: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "claim", "weakness", "attack", "persuasion", "plan", "angle", "evidence",
        "evidence_query", "tactic", "concession", "draft", "voiced", "reflection",
        "critic_verdict", "critic_score", "critic_pass", "memory_context", "worker", "final",
    )
    return {k: turn[k] for k in keys if k in turn and turn[k]}


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


def export_traces_json(traces: list[ArchitectureTrace], path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(t) for t in traces], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
