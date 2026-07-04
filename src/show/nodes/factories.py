"""Registre des nœuds cognitifs : factories ``persona -> node_fn(state, runtime)``.

Trois familles :
- ``listen`` : perception + mise à jour du mind (dérive, émotions, concession) ;
- nœuds de preuve (recherche web typée par le domaine) ;
- nœuds de pensée (raisonnement interne typé par le domaine), puis ``strategize``.
La mise en voix (``draft`` / ``voice`` / ``deliver``) est dans ``delivery.py``.
"""

from __future__ import annotations

from typing import Callable

from langgraph.runtime import Runtime

from agents.react.nodes.common import first_allowed_tactic, parse_labeled_lines
from config.show_config import HIGH_AROUSAL, SHOW_CONFIG
from show import llm, mind as mind_algo
from show.context import ShowContext, emit_event
from show.nodes import prompts
from show.personas.vector import AGGRESSIVE_TACTICS, PersonaVector
from show.state import ShowState, last_guest_entry

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
    "concede_then_refute": "concède avant de contrer",
    "draft": "construit son argument",
    "voice": "met en voix",
    "deliver": "prend la parole",
}


def _notify(runtime: Runtime[ShowContext], persona: PersonaVector, step: str) -> None:
    emit_event(
        runtime.context,
        {"type": "step", "agent": persona.agent_id, "step": step,
         "label": STEP_LABELS.get(step, step)},
    )


def _parse_score(raw: str) -> float:
    try:
        return max(0.0, min(10.0, float(raw.strip().split()[0]))) / 10.0
    except (ValueError, IndexError):
        return 0.3


def make_listen(persona: PersonaVector) -> NodeFn:
    def listen(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "listen")
        mind = state["minds"][persona.agent_id]
        opponent = last_guest_entry(state, exclude=persona.agent_id)

        if opponent is None:
            # Premier tour : pas de réplique adverse, on cadre le sujet.
            return {
                "turn": {
                    "claim": state["topic"],
                    "weakness": "cadrage du sujet encore ouvert — imposer sa lecture",
                    "attack": "none",
                    "persuasion": 0.0,
                    "must_concede": False,
                }
            }

        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.LISTEN_SYSTEM,
            prompts.listen_prompt(opponent["text"], state["topic"]),
            temperature=persona.temperature_facts,
        )
        parsed = parse_labeled_lines(text, ["CLAIM", "WEAKNESS", "ATTACK", "SCORE"])
        persuasion = _parse_score(parsed.get("score", ""))
        attack = (parsed.get("attack") or "argument").strip().lower()
        if attack not in ("personal", "moral"):
            attack = "argument"

        event = {"personal": "attacked_personal", "moral": "attacked_moral"}.get(
            attack, "argument"
        )
        mind = mind_algo.appraise(mind, persona, event)
        opponent_stance = state["minds"][opponent["speaker"]]["stance"]
        mind = mind_algo.revise_stance(mind, persona, opponent_stance, persuasion)
        mind = mind_algo.update_conviction(mind, persuasion, countered=False)
        if attack in ("personal", "moral"):
            mind["grudges"] = mind["grudges"] + [parsed.get("claim", opponent["text"][:120])]
        if persuasion >= 0.6:
            mind["beliefs"] = mind["beliefs"] + [parsed.get("claim", "")]

        must_concede = mind_algo.should_concede(persuasion, persona, runtime.context.rng())
        return {
            "minds": {**state["minds"], persona.agent_id: mind},
            "turn": {
                "claim": parsed.get("claim") or opponent["text"][:200],
                "weakness": parsed.get("weakness") or "contradiction non exposée",
                "attack": attack,
                "persuasion": persuasion,
                "must_concede": must_concede,
            },
        }

    return listen


# Nœuds de preuve : requête web typée par le style d'évidence du domaine.
_EVIDENCE_QUERIES: dict[str, Callable[[PersonaVector, ShowState], str]] = {
    "verify_facts": lambda p, s: (
        f"données chiffrées récentes et vérifiables 2025 : {s['turn'].get('claim', s['topic'])} "
        f"({p.specialization})"
    ),
    "recall_precedent": lambda p, s: (
        f"précédents historiques comparables et leurs conséquences : {s['topic']}"
    ),
    "quantify": lambda p, s: (
        f"études d'impact, coûts et chiffres macroéconomiques 2025 : {s['topic']}"
    ),
}


def make_evidence_node(name: str) -> NodeFactory:
    def factory(persona: PersonaVector) -> NodeFn:
        def node(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
            _notify(runtime, persona, name)
            ctx = runtime.context
            if not ctx.enable_web_search or ctx.client is None:
                return {"turn": {**state["turn"], "evidence": ""}}
            query = _EVIDENCE_QUERIES[name](persona, state)
            result = llm.search(ctx.client, ctx.model_internal or SHOW_CONFIG["model_internal"], query)
            if result.startswith("Erreur"):
                result = ""
            return {"turn": {**state["turn"], "evidence": result, "evidence_query": query}}

        return node

    return factory


# Nœuds de pensée : chaque domaine raisonne à sa manière.
_THINK_INSTRUCTIONS: dict[str, str] = {
    "hypothesize": (
        "En physicien : formule une hypothèse falsifiable qui ébranle la thèse adverse, "
        "en t'appuyant sur les ordres de grandeur et les preuves disponibles."
    ),
    "build_analogy": (
        "En historien : à partir du précédent trouvé, construis une analogie datée et "
        "précise qui éclaire le débat et piège la thèse adverse."
    ),
    "reframe_concept": (
        "En philosophe : redéfinis le concept central du débat et expose le présupposé "
        "caché de la thèse adverse."
    ),
    "find_contradiction": (
        "En philosophe : à partir de ce recadrage, expose la contradiction interne de la "
        "position adverse (ce qu'elle affirme contre ce qu'elle suppose)."
    ),
    "recall_anecdote": (
        "En écrivain : convoque une scène concrète, un personnage ou une anecdote incarnée "
        "qui rend la thèse adverse abstraite et désincarnée."
    ),
    "narrative_frame": (
        "En écrivain : transforme cette matière en un mini-récit avec un enjeu humain qui "
        "porte ta position."
    ),
    "quantify": (
        "En économiste : pose les ordres de grandeur du problème (coûts, bénéfices, qui "
        "paie, qui gagne) à partir des preuves disponibles."
    ),
    "model_tradeoff": (
        "En économiste : formule l'arbitrage coût/bénéfice que la thèse adverse ignore, "
        "et ce que révèlent les incitations des acteurs."
    ),
}


def make_think_node(name: str) -> NodeFactory:
    instruction = _THINK_INSTRUCTIONS[name]

    def factory(persona: PersonaVector) -> NodeFn:
        def node(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
            _notify(runtime, persona, name)
            mind = state["minds"][persona.agent_id]
            text = llm.think(
                runtime.context.model_internal or SHOW_CONFIG["model_internal"],
                prompts.THINK_SYSTEM,
                prompts.think_prompt(instruction, persona, mind, state["topic"], state["turn"]),
                temperature=persona.temperature_facts,
            )
            previous = state["turn"].get("angle", "")
            angle = f"{previous}\n{text}".strip() if previous else text
            return {"turn": {**state["turn"], "angle": angle}}

        return node

    return factory


def make_strategize(persona: PersonaVector) -> NodeFn:
    def strategize(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "strategize")
        mind = state["minds"][persona.agent_id]
        allowed = list(persona.tactics)
        # À chaud, les tactiques agressives passent en tête de liste.
        if mind["arousal"] > HIGH_AROUSAL:
            allowed.sort(key=lambda t: 0 if t in AGGRESSIVE_TACTICS else 1)
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.TACTIC_SYSTEM,
            prompts.tactic_prompt(persona, state["turn"], allowed),
            temperature=persona.temperature_facts,
        )
        parsed = parse_labeled_lines(text, ["TACTIC"])
        tactic = first_allowed_tactic(parsed.get("tactic", ""), allowed, allowed[0])
        return {"turn": {**state["turn"], "tactic": tactic}}

    return strategize


def make_concede_then_refute(persona: PersonaVector) -> NodeFn:
    def concede_then_refute(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "concede_then_refute")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.CONCEDE_SYSTEM,
            prompts.concede_prompt(persona, mind, state["topic"], state["turn"]),
            temperature=persona.temperature_facts,
        )
        return {
            "turn": {**state["turn"], "concession": text, "tactic": "concede_then_refute"}
        }

    return concede_then_refute
