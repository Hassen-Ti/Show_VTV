"""Helpers partagés par les factories cognitives et la pipeline de mise en voix."""

from __future__ import annotations

from typing import Callable

from langgraph.runtime import Runtime

from show.runtime.context import ShowContext, emit_event
from show.guests.personas.vector import PersonaVector
from show.memory.state import ShowState

NodeFn = Callable[[ShowState, Runtime[ShowContext]], dict]
NodeFactory = Callable[[PersonaVector], NodeFn]

STEP_LABELS = {
    "listen": "écoute l'adversaire",
    "verify_facts": "vérifie les faits",
    "hypothesize": "formule une hypothèse",
    "recall_precedent": "convoque un précédent",
    "build_analogy": "construit une analogie",
    "reframe_concept": "redéfinit les termes",
    "find_contradiction": "cherche la contradiction",
    "recall_anecdote": "se souvient d'une histoire",
    "narrative_frame": "met en récit",
    "quantify": "chiffre le problème",
    "model_tradeoff": "pèse l'arbitrage",
    "strategize": "choisit sa tactique",
    "plan": "établit un plan",
    "reflect": "réfléchit sur son brouillon",
    "revise_draft": "révise le brouillon",
    "critic_verify": "vérifie la solidité",
    "self_correct": "corrige son argument",
    "recall_memory": "rappelle ses souvenirs",
    "supervisor_route": "route vers un worker",
    "parallel_gather": "collecte preuves en parallèle",
    "concede_then_refute": "concède avant de contrer",
    "draft": "construit son argument",
    "voice": "met en voix",
    "deliver": "prend la parole",
}


def notify_step(runtime: Runtime[ShowContext], persona: PersonaVector, step: str) -> None:
    """Émet l'événement UI ``step`` pour un nœud cognitif ou de delivery."""
    emit_event(
        runtime.context,
        {
            "type": "step",
            "agent": persona.agent_id,
            "step": step,
            "label": STEP_LABELS.get(step, step),
        },
    )
