"""Benchmark : 10 architectures agentiques sur un même persona, évaluation comparative."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

import show.llm
from show.graph.show_graph import run_show
from show.personas.architectures import ARCHITECTURES
from show.personas.registry import make_guest, make_guest_with_architecture
from show.personas.trace import (
    ArchitectureTrace,
    build_pipeline,
    export_traces_json,
    show_state_snapshot,
    TraceRecorder,
)
from show.state import initial_show_state
from show.personas.vector import PersonaVector

BENCHMARK_PERSONA = {
    "personality": "provocateur",
    "domain": "physicien",
    "specialization": "intelligence artificielle",
    "stance": 0.75,
    "agent_id": "guest_a",
    "name": "Provocateur physicien (benchmark arch)",
}

BENCHMARK_OPPONENT = {
    "personality": "diplomate",
    "domain": "philosophe",
    "specialization": "éthique des techniques",
    "stance": -0.6,
    "agent_id": "guest_b",
}

TOPIC = "Faut-il ralentir le déploiement de l'IA ?"


@dataclass(frozen=True)
class ArchitectureEvalRow:
    rank: int
    architecture_id: str
    architecture_name: str
    source: str
    reference: str
    cognitive_sequence: str
    steps_executed: int
    tactic_valid: bool
    tactic_used: str
    evidence_used: bool
    monologue_ok: bool
    transcript_words: int
    transcript_chars: int
    tension_final: float
    stance_drift: float
    has_reflection: bool
    has_plan: bool
    critic_pass: bool | None
    agent_pass: bool
    quality_score: float


def _personality_aware_think(persona: PersonaVector) -> Callable[..., str]:
    arch = persona.architecture_id

    def think(model, system, user, *, temperature, max_tokens=None):
        if "SCORE" in system:
            return (
                f"CLAIM: Thèse adverse sur {persona.specialization}.\n"
                f"WEAKNESS: Angle {persona.domain} non étayé.\n"
                f"ATTACK: argument\nSCORE: 7"
            )
        if "TACTIC" in system:
            return f"TACTIC: {persona.tactics[0]}"
        if "monologue intérieur" in system:
            return f"[{arch}] Je cache plus que je ne montre sur {persona.specialization}."
        if "Planifie" in system or "plan" in system.lower() and "étapes" in system:
            return "1. Percevoir la faille.\n2. Chercher une preuve.\n3. Frapper avec l'hypothèse."
        if "Critique le brouillon" in system or "failles" in system:
            return "Mon angle manque de chiffre ; je dois resserrer la punchline."
        if "VERDICT" in system or "solidité" in system:
            draft = "brouillon"  # mock
            if "brouillon" in user.lower() or len(user) > 200:
                return "VERDICT: pass\nSCORE: 8"
            return "VERDICT: revise\nSCORE: 5"
        if "Corrige le brouillon" in system:
            return (
                f"{persona.opener} version corrigée sur {persona.specialization} "
                f"({arch}/{persona.domain})."
            )
        return (
            f"{persona.opener} [{arch}] argument {persona.evidence_style} "
            f"— {persona.specialization}."
        )

    return think


def _score_response(
    persona: PersonaVector,
    result: dict,
    events: list[dict],
    *,
    sim_pass: bool,
) -> ArchitectureEvalRow:
    entry = next(e for e in result["transcript"] if e["speaker"] == persona.agent_id)
    steps = [e for e in events if e.get("type") == "step" and e.get("agent") == persona.agent_id]
    step_names = {e["step"] for e in steps}
    turn = result.get("turn") or {}
    history = result["stance_history"].get(persona.agent_id, [])
    stance_drift = abs(history[-1] - history[0]) if len(history) >= 2 else 0.0
    monologue = result["minds"][persona.agent_id]["inner_monologue"]
    monologue_ok = bool(monologue) and monologue not in entry["text"]
    words = len(entry["text"].split())

    has_plan = "plan" in step_names
    has_reflection = "reflect" in step_names
    critic_ran = "critic_verify" in step_names
    critic_pass_val = turn.get("critic_pass") if critic_ran else None

    quality = 0.0
    quality += 0.20 if sim_pass else 0.0
    quality += 0.12 if entry["tactic"] in persona.tactics else 0.0
    quality += 0.08 if entry["evidence_used"] else 0.02
    quality += 0.08 if monologue_ok else 0.0
    quality += 0.08 * min(1.0, words / 15.0)
    quality += 0.06 * min(1.0, result.get("tension", 0) * 2)
    quality += 0.02 * min(1.0, len(steps) / 10.0)

    arch_bonuses = {
        "react": 0.05 if {"listen", "verify_facts", "hypothesize"} <= step_names else 0.0,
        "reflexion": 0.08 if {"reflect", "revise_draft"} <= step_names else 0.0,
        "plan_execute": 0.08 if has_plan else 0.0,
        "rewoo": 0.07 if has_plan else 0.0,
        "verifier_critic": 0.07 if critic_ran else 0.0,
        "self_rag": 0.08 if critic_ran and "revise_draft" in step_names else 0.04 if critic_ran else 0.0,
        "memory_augmented": 0.07 if "recall_memory" in step_names else 0.0,
        "supervisor_worker": 0.07 if "supervisor_route" in step_names else 0.0,
        "parallel_dag": 0.07 if "parallel_gather" in step_names else 0.0,
        "correction_loop": 0.07 if "self_correct" in step_names else 0.0,
    }
    quality += arch_bonuses.get(persona.architecture_id, 0.0)

    spec = ARCHITECTURES[persona.architecture_id]
    return ArchitectureEvalRow(
        rank=0,
        architecture_id=persona.architecture_id,
        architecture_name=spec.name,
        source=spec.source,
        reference=spec.reference,
        cognitive_sequence="→".join(persona.cognitive_sequence),
        steps_executed=len(steps),
        tactic_valid=entry["tactic"] in persona.tactics,
        tactic_used=entry["tactic"],
        evidence_used=entry["evidence_used"],
        monologue_ok=monologue_ok,
        transcript_words=words,
        transcript_chars=len(entry["text"]),
        tension_final=round(result.get("tension", 0.0), 4),
        stance_drift=round(stance_drift, 4),
        has_reflection=has_reflection,
        has_plan=has_plan,
        critic_pass=critic_pass_val,
        agent_pass=sim_pass,
        quality_score=round(quality, 4),
    )


def evaluate_architecture_with_trace(architecture_id: str) -> tuple[ArchitectureEvalRow, ArchitectureTrace]:
    guest_a = make_guest_with_architecture(
        **{k: v for k, v in BENCHMARK_PERSONA.items() if k != "agent_id"},
        agent_id=BENCHMARK_PERSONA["agent_id"],
        architecture_id=architecture_id,
    )
    guest_b = make_guest(
        BENCHMARK_OPPONENT["personality"],
        BENCHMARK_OPPONENT["domain"],
        BENCHMARK_OPPONENT["specialization"],
        BENCHMARK_OPPONENT["stance"],
        agent_id=BENCHMARK_OPPONENT["agent_id"],
    )

    think_fn = _personality_aware_think(guest_a)
    recorder = TraceRecorder(think_fn)
    original_think = show.llm.think
    original_search = show.llm.search
    show.llm.think = recorder.think
    show.llm.search = lambda client, model, query: f"Source {guest_a.evidence_style} 2026 — {query[:40]}."
    show_initial = show_state_snapshot(initial_show_state(TOPIC, [guest_a, guest_b], 1))

    try:
        result = run_show(
            TOPIC,
            guest_a,
            guest_b,
            max_rounds=1,
            client=None,
            enable_web_search=False,
            emit=recorder.emit,
            trace_llm_cursor=recorder.llm_cursor,
        )
        sim_pass = any(e["speaker"] == guest_a.agent_id for e in result["transcript"])
    finally:
        show.llm.think = original_think
        show.llm.search = original_search

    row = _score_response(guest_a, result, recorder.events, sim_pass=sim_pass)
    entry = next(e for e in result["transcript"] if e["speaker"] == guest_a.agent_id)
    spec = ARCHITECTURES[architecture_id]
    mind = result["minds"][guest_a.agent_id]

    trace = ArchitectureTrace(
        architecture_id=architecture_id,
        architecture_name=spec.name,
        source=spec.source,
        reference=spec.reference,
        cognitive_sequence="→".join(guest_a.cognitive_sequence),
        persona_name=guest_a.name,
        personality=guest_a.personality,
        domain=guest_a.domain,
        topic=TOPIC,
        quality_score=row.quality_score,
        agents=[
            {
                "id": guest_a.agent_id,
                "name": guest_a.name,
                "role": "guest",
                "personality": guest_a.personality,
                "architecture_id": guest_a.architecture_id,
            },
            {
                "id": guest_b.agent_id,
                "name": guest_b.name,
                "role": "guest",
                "personality": guest_b.personality,
                "architecture_id": guest_b.architecture_id,
            },
            {"id": "moderator", "name": "Mr Bullshit", "role": "moderator"},
        ],
        pipeline=build_pipeline(recorder.events, recorder.llm_calls),
        show_initial=show_initial,
        show_final=show_state_snapshot(result),
        llm_calls=recorder.llm_calls,
        events=recorder.events,
        on_air_response=entry["text"],
        inner_monologue=mind.get("inner_monologue", ""),
        tactic_used=entry["tactic"],
        evidence_used=entry["evidence_used"],
        tension_final=round(result.get("tension", 0.0), 4),
    )
    return row, trace


def evaluate_architecture(architecture_id: str) -> ArchitectureEvalRow:
    row, _ = evaluate_architecture_with_trace(architecture_id)
    return row


def run_architecture_benchmark() -> list[ArchitectureEvalRow]:
    rows, _ = run_architecture_benchmark_with_traces()
    return rows


def run_architecture_benchmark_with_traces() -> tuple[list[ArchitectureEvalRow], list[ArchitectureTrace]]:
    pairs = [evaluate_architecture_with_trace(aid) for aid in ARCHITECTURES]
    pairs.sort(key=lambda p: p[0].quality_score, reverse=True)
    rows = [ArchitectureEvalRow(**{**asdict(p[0]), "rank": i + 1}) for i, p in enumerate(pairs)]
    traces = []
    for i, (_, trace) in enumerate(pairs):
        trace.rank = i + 1
        traces.append(trace)
    return rows, traces


def export_csv(rows: list[ArchitectureEvalRow], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dicts = [asdict(r) for r in rows]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
        writer.writeheader()
        writer.writerows(dicts)
    return path


def export_json(rows: list[ArchitectureEvalRow], path: Path) -> Path:
    path.write_text(json.dumps([asdict(r) for r in rows], indent=2, ensure_ascii=False), encoding="utf-8")
    return path
