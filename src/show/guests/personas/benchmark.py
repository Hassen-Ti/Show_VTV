"""Benchmark personnalité × domaine : scores traits + simulation agent mockée."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from show.graph.show_graph import run_show
from show.memory.mind import (
    appraise,
    compute_tension,
    decay,
    effective_sentence_max,
    effective_voice_temperature,
    revise_stance,
    should_concede,
)
from show.guests.personas.registry import DOMAINS, PERSONALITIES, make_guest, persona_style_hints
from show.guests.personas.vector import AGGRESSIVE_TACTICS, PersonaVector
from show.memory.state import initial_mind

# Spécialisations réalistes par couple (personnalité, domaine).
SPECIALIZATIONS: dict[tuple[str, str], str] = {
    ("provocateur", "physicien"): "intelligence artificielle",
    ("provocateur", "historien"): "propagande numérique",
    ("provocateur", "philosophe"): "libertés individuelles",
    ("provocateur", "ecrivain"): "art génératif",
    ("provocateur", "economiste"): "IA et emploi",
    ("diplomate", "physicien"): "énergie et climat",
    ("diplomate", "historien"): "mémoire collective",
    ("diplomate", "philosophe"): "éthique des techniques",
    ("diplomate", "ecrivain"): "récit politique",
    ("diplomate", "economiste"): "transition sociale",
    ("cerebral", "physicien"): "physique quantique",
    ("cerebral", "historien"): "sécurité publique",
    ("cerebral", "philosophe"): "pédagogie numérique",
    ("cerebral", "ecrivain"): "esthétique algorithmique",
    ("cerebral", "economiste"): "modèles macro",
}

EVIDENCE_SCORES = {
    "empirical": 0.95,
    "precedent": 0.85,
    "dialectic": 0.90,
    "narrative": 0.75,
    "formal": 0.88,
}

CONCLAVE_ROLES = {
    "provocateur": "Le Flux",
    "diplomate": "Le Protocole",
    "cerebral": "L'Archive",
}

BENCHMARK_TOPIC = "Faut-il ralentir le déploiement de l'IA ?"

# Deux adversaires standards pour stress-test multi-scénario.
OPPONENTS: tuple[tuple[str, str, str, float], ...] = (
    ("diplomate", "philosophe", "éthique des techniques", -0.6),
    ("provocateur", "physicien", "intelligence artificielle", 0.8),
    ("cerebral", "historien", "sécurité publique", 0.6),
)


@dataclass(frozen=True)
class TraitScores:
    clash_index: float
    adaptability: float
    stability: float
    cognitive_depth: float
    evidence_rigor: float
    voice_expressivity: float
    concession_readiness: float
    mind_volatility: float


@dataclass(frozen=True)
class AgentSimResult:
    tactic_valid: bool
    tactic_used: str
    tension_final: float
    stance_drift: float
    opponent_drift: float
    monologue_ok: bool
    transcript_words: int
    cognitive_steps: int
    agent_pass: bool
    opponent_id: str


@dataclass(frozen=True)
class PersonaBenchmarkRow:
    rank: int
    persona_id: str
    personality: str
    domain: str
    specialization: str
    conclave_role: str
    display_name: str
    stance_default: float
    trait_clash: float
    trait_adaptability: float
    trait_stability: float
    trait_cognitive_depth: float
    trait_evidence_rigor: float
    trait_voice_expressivity: float
    trait_concession_readiness: float
    trait_mind_volatility: float
    trait_composite: float
    agent_tactic_valid: bool
    agent_tactic_used: str
    agent_tension_final: float
    agent_stance_drift: float
    agent_opponent_drift: float
    agent_monologue_ok: bool
    agent_transcript_words: int
    agent_pass: bool
    agent_composite: float
    agent_scenarios_passed: int
    final_score: float
    preset_used_in: str
    voice_hint: str
    cognitive_sequence: str
    tactics: str


def all_persona_combos() -> list[tuple[str, str]]:
    return [(p, d) for p in PERSONALITIES for d in DOMAINS]


def build_persona(
    personality: str,
    domain: str,
    *,
    agent_id: str = "guest_a",
    stance: Optional[float] = None,
) -> PersonaVector:
    spec = SPECIALIZATIONS.get((personality, domain), f"{domain} appliqué")
    if stance is None:
        stance = 0.75 if personality == "provocateur" else -0.55 if personality == "diplomate" else 0.35
    return make_guest(personality, domain, spec, stance, agent_id=agent_id)


def score_traits(persona: PersonaVector) -> TraitScores:
    aggressive = sum(1 for t in persona.tactics if t in AGGRESSIVE_TACTICS)
    clash = persona.arousal_gain * (aggressive / max(len(persona.tactics), 1))
    adaptability = persona.concession_rate * (1.0 - persona.stubbornness)
    stability = persona.stubbornness * persona.initial_conviction
    cognitive_depth = len(persona.cognitive_sequence) / 5.0
    evidence_rigor = EVIDENCE_SCORES.get(persona.evidence_style, 0.5)
    voice_expressivity = min(1.0, persona.temperature_voice / 1.5)
    concession_readiness = persona.concession_rate

    mind = initial_mind(persona)
    heated = appraise(mind, persona, "attacked_moral")
    cooled = decay(heated, persona)
    volatility = abs(heated["arousal"] - cooled["arousal"]) + abs(heated["valence"] - cooled["valence"])

    return TraitScores(
        clash_index=round(clash, 4),
        adaptability=round(adaptability, 4),
        stability=round(stability, 4),
        cognitive_depth=round(cognitive_depth, 4),
        evidence_rigor=round(evidence_rigor, 4),
        voice_expressivity=round(voice_expressivity, 4),
        concession_readiness=round(concession_readiness, 4),
        mind_volatility=round(min(1.0, volatility), 4),
    )


def _trait_composite(t: TraitScores, personality: str) -> float:
    """Pondération par archétype — spectacle vs nuance."""
    weights = {
        "provocateur": (0.25, 0.10, 0.10, 0.10, 0.10, 0.20, 0.05, 0.10),
        "diplomate": (0.10, 0.25, 0.15, 0.15, 0.15, 0.10, 0.20, 0.05),
        "cerebral": (0.10, 0.15, 0.15, 0.20, 0.20, 0.05, 0.10, 0.15),
    }
    w = weights[personality]
    vals = (
        t.clash_index,
        t.adaptability,
        t.stability,
        t.cognitive_depth,
        t.evidence_rigor,
        t.voice_expressivity,
        t.concession_readiness,
        t.mind_volatility,
    )
    return round(sum(a * b for a, b in zip(vals, w)), 4)


def make_personality_aware_think(persona: PersonaVector) -> Callable[..., str]:
    """LLM mock qui répond selon la personnalité testée."""

    def think(model, system, user, *, temperature, max_tokens=None):
        if "SCORE" in system:
            base = 6 if persona.personality == "diplomate" else 8 if persona.personality == "provocateur" else 7
            return (
                f"CLAIM: Position {persona.specialization}.\n"
                f"WEAKNESS: Angle {persona.domain}.\n"
                f"ATTACK: via {persona.evidence_style}\n"
                f"SCORE: {base}"
            )
        if "TACTIC" in system:
            return f"TACTIC: {persona.tactics[0]}"
        if "monologue intérieur" in system:
            hints = persona_style_hints(persona)
            return f"[{persona.personality}] {hints[0]} — doute interne sur {persona.specialization}."
        opener = persona.opener
        return (
            f"{opener} argument {persona.evidence_style} "
            f"sur {persona.specialization} ({persona.personality}/{persona.domain})."
        )

    return think


def simulate_agent_show(
    persona: PersonaVector,
    *,
    think_fn: Callable[..., str],
    opponent_spec: tuple[str, str, str, float],
) -> AgentSimResult:
    """Un round agent mocké : persona en guest_a vs opposant donné."""
    opp = make_guest(
        opponent_spec[0],
        opponent_spec[1],
        opponent_spec[2],
        opponent_spec[3],
        agent_id="guest_b",
    )

    import show.llm

    original_think = show.llm.think
    original_search = show.llm.search
    show.llm.think = think_fn
    show.llm.search = lambda client, model, query: f"Source {persona.evidence_style} 2026."

    try:
        result = run_show(
            BENCHMARK_TOPIC,
            persona,
            opp,
            max_rounds=1,
            client=None,
            enable_web_search=False,
            emit=lambda _: None,
        )
    finally:
        show.llm.think = original_think
        show.llm.search = original_search

    guest_entries = [e for e in result["transcript"] if e["speaker"] == persona.agent_id]
    entry = guest_entries[0] if guest_entries else None
    tactic_used = entry["tactic"] if entry else ""
    tactic_valid = tactic_used in persona.tactics if entry else False
    history = result["stance_history"].get(persona.agent_id, [])
    stance_drift = abs(history[-1] - history[0]) if len(history) >= 2 else 0.0
    opp_history = result["stance_history"].get("guest_b", [])
    opponent_drift = abs(opp_history[-1] - opp_history[0]) if len(opp_history) >= 2 else 0.0
    monologue = result["minds"][persona.agent_id]["inner_monologue"]
    monologue_ok = bool(monologue) and all(monologue not in e["text"] for e in result["transcript"])
    words = len(entry["text"].split()) if entry else 0

    agent_pass = tactic_valid and monologue_ok and words >= 3

    return AgentSimResult(
        tactic_valid=tactic_valid,
        tactic_used=tactic_used,
        tension_final=round(result.get("tension", 0.0), 4),
        stance_drift=round(stance_drift, 4),
        opponent_drift=round(opponent_drift, 4),
        monologue_ok=monologue_ok,
        transcript_words=words,
        cognitive_steps=len(persona.cognitive_sequence),
        agent_pass=agent_pass,
        opponent_id=f"{opponent_spec[0]}_{opponent_spec[1]}",
    )


def _agent_composite(sim: AgentSimResult, traits: TraitScores, personality: str) -> float:
    influence = min(1.0, sim.opponent_drift * 3.0)
    concession_bonus = 0.08 if personality == "diplomate" and sim.tactic_used == "concede_then_refute" else 0.0
    return round(
        (0.25 if sim.agent_pass else 0.0)
        + 0.18 * min(1.0, sim.tension_final * 1.2)
        + 0.12 * min(1.0, sim.stance_drift * 2.0)
        + 0.18 * influence
        + 0.12 * traits.cognitive_depth
        + 0.08 * (1.0 if sim.monologue_ok else 0.0)
        + 0.07 * min(1.0, sim.transcript_words / 20.0)
        + concession_bonus,
        4,
    )


def simulate_agent_multi(
    persona: PersonaVector,
    *,
    think_fn: Callable[..., str],
) -> tuple[AgentSimResult, ...]:
    return tuple(
        simulate_agent_show(persona, think_fn=think_fn, opponent_spec=opp)
        for opp in OPPONENTS
    )


def _preset_label(personality: str, domain: str) -> str:
    for key, preset in _import_presets().items():
        for slot in (preset.guest_a, preset.guest_b):
            if slot.personality == personality and slot.domain == domain:
                return preset.label if key else "Débat libre"
    return ""


def _import_presets():
    from config.show_presets import SHOW_PRESETS

    return SHOW_PRESETS


def run_full_benchmark() -> list[PersonaBenchmarkRow]:
    rows: list[PersonaBenchmarkRow] = []

    for personality, domain in all_persona_combos():
        persona = build_persona(personality, domain)
        traits = score_traits(persona)
        trait_comp = _trait_composite(traits, personality)
        sims = simulate_agent_multi(persona, think_fn=make_personality_aware_think(persona))
        agent_comps = [_agent_composite(s, traits, personality) for s in sims]
        agent_comp = round(sum(agent_comps) / len(agent_comps), 4)
        sim = sims[0]
        scenarios_passed = sum(1 for s in sims if s.agent_pass)
        avg_tension = round(sum(s.tension_final for s in sims) / len(sims), 4)
        avg_opp_drift = round(sum(s.opponent_drift for s in sims) / len(sims), 4)
        avg_stance_drift = round(sum(s.stance_drift for s in sims) / len(sims), 4)
        final = round(0.40 * trait_comp + 0.60 * agent_comp, 4)
        voice_hint, _ = persona_style_hints(persona)

        rows.append(
            PersonaBenchmarkRow(
                rank=0,
                persona_id=f"{personality}_{domain}",
                personality=personality,
                domain=domain,
                specialization=persona.specialization,
                conclave_role=CONCLAVE_ROLES[personality],
                display_name=persona.name,
                stance_default=persona.initial_stance,
                trait_clash=traits.clash_index,
                trait_adaptability=traits.adaptability,
                trait_stability=traits.stability,
                trait_cognitive_depth=traits.cognitive_depth,
                trait_evidence_rigor=traits.evidence_rigor,
                trait_voice_expressivity=traits.voice_expressivity,
                trait_concession_readiness=traits.concession_readiness,
                trait_mind_volatility=traits.mind_volatility,
                trait_composite=trait_comp,
                agent_tactic_valid=all(s.tactic_valid for s in sims),
                agent_tactic_used=sim.tactic_used,
                agent_tension_final=avg_tension,
                agent_stance_drift=avg_stance_drift,
                agent_opponent_drift=avg_opp_drift,
                agent_monologue_ok=all(s.monologue_ok for s in sims),
                agent_transcript_words=round(sum(s.transcript_words for s in sims) / len(sims)),
                agent_pass=scenarios_passed == len(sims),
                agent_composite=agent_comp,
                agent_scenarios_passed=scenarios_passed,
                final_score=final,
                preset_used_in=_preset_label(personality, domain),
                voice_hint=voice_hint,
                cognitive_sequence="→".join(persona.cognitive_sequence),
                tactics="|".join(persona.tactics),
            )
        )

    rows.sort(key=lambda r: r.final_score, reverse=True)
    ranked = [PersonaBenchmarkRow(**{**asdict(r), "rank": i + 1}) for i, r in enumerate(rows)]
    return ranked


def top_n(rows: list[PersonaBenchmarkRow], n: int = 10) -> list[PersonaBenchmarkRow]:
    return rows[:n]


def top10_balanced_cast(rows: list[PersonaBenchmarkRow]) -> list[PersonaBenchmarkRow]:
    """Top 10 pour casting plateau : 4 Flux + 3 Archive + 3 Protocole."""
    quotas = {"provocateur": 4, "cerebral": 3, "diplomate": 3}
    picked: list[PersonaBenchmarkRow] = []
    for personality, limit in quotas.items():
        pool = [r for r in rows if r.personality == personality]
        picked.extend(pool[:limit])
    return picked


def rows_to_dicts(rows: list[PersonaBenchmarkRow]) -> list[dict[str, Any]]:
    return [asdict(r) for r in rows]


def export_csv(rows: list[PersonaBenchmarkRow], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    dicts = rows_to_dicts(rows)
    if not dicts:
        return path
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
        writer.writeheader()
        writer.writerows(dicts)
    return path


def export_json(rows: list[PersonaBenchmarkRow], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows_to_dicts(rows), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def mind_micro_benchmark(persona: PersonaVector) -> dict[str, Any]:
    """Tests algorithmiques purs (complément agent)."""
    mind = initial_mind(persona)
    revised = revise_stance(mind, persona, opponent_stance=-mind["stance"], persuasion=0.85)
    concede_strong = should_concede(0.9, persona, rand=0.99)
    concede_weak = should_concede(0.1, persona, rand=0.99)
    hot = appraise(mind, persona, "attacked_moral")
    voice_hot = effective_voice_temperature(hot, persona)
    voice_cold = effective_voice_temperature(mind, persona)
    return {
        "stance_revision_delta": round(abs(revised["stance"] - mind["stance"]), 4),
        "concedes_under_pressure": concede_strong,
        "concedes_randomly": concede_weak,
        "voice_temp_delta": round(voice_hot - voice_cold, 4),
        "sentence_max_hot": effective_sentence_max(hot, persona, 0.75),
        "sentence_max_cold": effective_sentence_max(mind, persona, 0.75),
    }
