"""Lab réflexion solo : un philosophe, N questions, traces complètes sans débat."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import show.llm
from config.show_config import SHOW_CONFIG
from show.context import ShowContext
from show.graph.guest_subgraph import build_guest_subgraph
from show.personas.registry import make_guest_with_architecture
from show.personas.trace import (
    build_pipeline,
    show_state_snapshot,
    TraceRecorder,
    turn_outputs_from_state,
)
from show.state import initial_show_state

PHILOSOPHER_QUESTIONS: tuple[str, ...] = (
    "La liberté est-elle compatible avec le déterminisme, ou n'est-ce qu'une illusion utile ?",
    "Peut-on fonder une éthique rigoureuse sans recourir à Dieu ni à la métaphysique ?",
    "Qu'est-ce qui distingue une expérience vécue d'une simple information traitée par le cerveau ?",
    "Le langage façonne-t-il la pensée, ou se contente-t-il de la traduire ?",
    "Une société juste exige-t-elle l'égalité des chances ou l'égalité des résultats ?",
    "Une conscience artificielle pourrait-elle être de même nature que la conscience humaine ?",
    "Le progrès technique implique-t-il nécessairement un progrès moral ?",
    "Faut-il préférer une vérité désagréable à une illusion réconfortante ?",
    "Le temps existe-t-il indépendamment des choses qui changent ?",
    "Restons-nous la même personne après une transformation profonde de nos croyances ?",
)


@dataclass
class QuestionTrace:
    question_id: int
    question: str
    final_response: str
    inner_monologue: str
    all_outputs: dict[str, Any]
    pipeline: list
    turn_final: dict[str, Any] = field(default_factory=dict)
    mind_final: dict[str, Any] = field(default_factory=dict)
    show_initial: dict[str, Any] = field(default_factory=dict)
    show_final: dict[str, Any] = field(default_factory=dict)
    llm_calls: list = field(default_factory=list)


@dataclass
class PhilosopherLabTrace:
    persona_name: str
    personality: str
    domain: str
    architecture_id: str
    cognitive_sequence: str
    specialization: str
    questions: list[QuestionTrace] = field(default_factory=list)


def make_philosopher_persona():
    """Philosophe cérébral, architecture Reflexion — réflexion pure, sans clash plateau."""
    return make_guest_with_architecture(
        "cerebral",
        "philosophe",
        "éthique et métaphysique",
        stance=0.0,
        architecture_id="reflexion",
        agent_id="philosopher",
        name="Philosophe réflexif",
    )


def _philosopher_think(question: str):
    """Mock LLM : réponses de réflexion philosophique (pas de clash TV)."""

    def think(model, system, user, *, temperature, max_tokens=None):
        q = question
        short = q[:72]

        if "SCORE" in system:
            return (
                f"CLAIM: « {short} » repose sur des présupposés non examinés.\n"
                f"WEAKNESS: La formulation binaire masque une distinction conceptuelle.\n"
                f"ATTACK: argument\nSCORE: 3"
            )
        if "redéfinis" in system or "présupposé" in system:
            return (
                f"[reframe] Avant de répondre à « {short} », il faut distinguer le sens ordinaire "
                f"du sens philosophique des termes centraux. L'ambiguïté n'est pas un obstacle "
                f"— c'est le lieu même de la pensée."
            )
        if "contradiction" in system or "contradiction interne" in (user or ""):
            return (
                f"[dialectique] La question « {short} » fait entrer en tension deux intuitions "
                f"que nous tenons simultanément. L'incohérence est dans le cadre, pas seulement "
                f"dans la réponse."
            )
        if "TACTIC" in system:
            return "TACTIC: reframe"
        if "Critique le brouillon" in system:
            return (
                "Le brouillon conclut trop vite. Il manque la suspension du jugement "
                "et l'explicitation des présupposés."
            )
        if "Corrige le brouillon" in system:
            return (
                f"Reprenons avec rigueur : sur « {short} », la réponse honnête commence "
                f"par reformuler la question plutôt que par trancher."
            )
        if "monologue intérieur" in system:
            return (
                f"[réflexion privée] Cette question touche à {short}. "
                f"Je dois résister à la rhétorique et tenir la nuance jusqu'au bout."
            )
        if "brouillon interne" in system:
            return (
                f"Thèse provisoire : « {q} » n'appelle pas une réponse oui/non, "
                f"mais une clarification de ce que nous entendons par les concepts en jeu. "
                f"La prudence conceptuelle précède la conclusion."
            )
        if "Applique la voix" in system:
            return (
                f"Reprenons les termes du problème. Face à « {short} », "
                f"la pensée doit d'abord cartographier les présupposés avant d'affirmer quoi que ce soit."
            )
        if "réplique finale" in system:
            return (
                f"Reprenons les termes du problème. {q} "
                f"ne reçoit de réponse satisfaisante qu'après avoir déplacé la question elle-même. "
                f"Ce n'est pas d'une certitude absolue que nous manquons, mais d'une clarification "
                f"des conditions sous lesquelles une réponse pourrait avoir un sens. "
                f"Ainsi formulée, l'honnêteté philosophique consiste peut-être à habiter l'énigme "
                f"plutôt qu'à la refermer."
            )
        if "raisonnement interne" in system:
            return (
                f"Analyse conceptuelle de « {short} » : les distinctions fines "
                f"précèdent toute affirmation définitive."
            )
        return f"Réflexion philosophique sur : {short}"

    return think


def _collect_all_outputs(pipeline: list, turn: dict[str, Any]) -> dict[str, Any]:
    """Agrège chaque sortie produite par étape + tour final."""
    by_step: dict[str, Any] = {}
    for step in pipeline:
        out = step.output if hasattr(step, "output") else step.get("output", {})
        if out:
            by_step[step.step if hasattr(step, "step") else step["step"]] = out
    merged = turn_outputs_from_state(turn)
    return {"par_etape": by_step, "tour_final": merged}


def run_single_question(
    persona,
    question: str,
    question_id: int,
) -> QuestionTrace:
    recorder = TraceRecorder(_philosopher_think(question))
    original_think = show.llm.think
    show.llm.think = recorder.think

    show_initial = show_state_snapshot(initial_show_state(question, [persona], max_rounds=1))
    compiled = build_guest_subgraph(persona)
    context = ShowContext(
        client=None,
        model_internal=SHOW_CONFIG["model_internal"],
        model_delivery=SHOW_CONFIG["model_delivery"],
        enable_web_search=False,
        emit=recorder.emit,
        trace_llm_cursor=recorder.llm_cursor,
    )

    try:
        state = initial_show_state(question, [persona], max_rounds=1)
        result = compiled.invoke(state, context=context)
    finally:
        show.llm.think = original_think

    pipeline = build_pipeline(recorder.events, recorder.llm_calls)
    turn = dict(result.get("turn") or {})
    mind = result["minds"][persona.agent_id]
    final = turn.get("final") or ""
    if not final:
        for entry in reversed(result.get("transcript") or []):
            if entry["speaker"] == persona.agent_id:
                final = entry["text"]
                break

    return QuestionTrace(
        question_id=question_id,
        question=question,
        final_response=final,
        inner_monologue=mind.get("inner_monologue", ""),
        all_outputs=_collect_all_outputs(pipeline, turn),
        pipeline=pipeline,
        turn_final=turn_outputs_from_state(turn),
        mind_final={
            "stance": mind.get("stance"),
            "conviction": mind.get("conviction"),
            "valence": mind.get("valence"),
            "arousal": mind.get("arousal"),
            "beliefs": list(mind.get("beliefs", [])),
            "grudges": list(mind.get("grudges", [])),
            "inner_monologue": mind.get("inner_monologue", ""),
        },
        show_initial=show_initial,
        show_final=show_state_snapshot(result),
        llm_calls=recorder.llm_calls,
    )


def run_philosopher_lab(
    questions: tuple[str, ...] | None = None,
) -> PhilosopherLabTrace:
    persona = make_philosopher_persona()
    qs = questions or PHILOSOPHER_QUESTIONS
    traces = [
        run_single_question(persona, q, i + 1)
        for i, q in enumerate(qs)
    ]
    return PhilosopherLabTrace(
        persona_name=persona.name,
        personality=persona.personality,
        domain=persona.domain,
        architecture_id=persona.architecture_id,
        cognitive_sequence="→".join(persona.cognitive_sequence),
        specialization=persona.specialization,
        questions=traces,
    )


def export_philosopher_json(lab: PhilosopherLabTrace, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(lab), indent=2, ensure_ascii=False), encoding="utf-8")
    return path
