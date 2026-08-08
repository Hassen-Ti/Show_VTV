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

from show.parsing import first_allowed_tactic, parse_labeled_lines
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


def make_plan(persona: PersonaVector) -> NodeFn:
    def plan(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "plan")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.PLAN_SYSTEM,
            prompts.plan_prompt(persona, mind, state["topic"], state["turn"]),
            temperature=persona.temperature_facts,
        )
        return {"turn": {**state["turn"], "plan": text}}

    return plan


def make_reflect(persona: PersonaVector) -> NodeFn:
    def reflect(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "reflect")
        mind = state["minds"][persona.agent_id]
        draft = state["turn"].get("draft", "")
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.REFLECT_SYSTEM,
            prompts.reflect_prompt(persona, mind, state["topic"], draft),
            temperature=persona.temperature_facts,
        )
        return {"turn": {**state["turn"], "reflection": text}}

    return reflect


def make_revise_draft(persona: PersonaVector) -> NodeFn:
    def revise_draft(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "revise_draft")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.CORRECT_SYSTEM,
            prompts.correct_prompt(
                persona, mind, state["topic"],
                state["turn"].get("draft", ""),
                state["turn"].get("reflection", ""),
            ),
            temperature=persona.temperature_facts,
        )
        return {"turn": {**state["turn"], "draft": text or state["turn"].get("draft", "")}}

    return revise_draft


def make_critic_verify(persona: PersonaVector) -> NodeFn:
    def critic_verify(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "critic_verify")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.CRITIC_SYSTEM,
            prompts.critic_prompt(persona, mind, state["topic"], state["turn"]),
            temperature=0.2,
        )
        parsed = parse_labeled_lines(text, ["VERDICT", "SCORE"])
        verdict = (parsed.get("verdict") or "pass").strip().lower()
        try:
            score = float((parsed.get("score") or "7").strip().split()[0]) / 10.0
        except (ValueError, IndexError):
            score = 0.7
        critic_pass = verdict == "pass" and score >= 0.6
        return {
            "turn": {
                **state["turn"],
                "critic_verdict": verdict,
                "critic_score": score,
                "critic_pass": critic_pass,
            }
        }

    return critic_verify


def make_self_correct(persona: PersonaVector) -> NodeFn:
    def self_correct(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "self_correct")
        mind = state["minds"][persona.agent_id]
        text = llm.think(
            runtime.context.model_internal or SHOW_CONFIG["model_internal"],
            prompts.CORRECT_SYSTEM,
            prompts.correct_prompt(
                persona, mind, state["topic"],
                state["turn"].get("draft", ""),
                state["turn"].get("reflection", ""),
            ),
            temperature=persona.temperature_facts,
        )
        return {"turn": {**state["turn"], "draft": text or state["turn"].get("draft", "")}}

    return self_correct


def make_recall_memory(persona: PersonaVector) -> NodeFn:
    def recall_memory(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "recall_memory")
        mind = state["minds"][persona.agent_id]
        memory = {
            "beliefs": mind["beliefs"][-5:],
            "grudges": mind["grudges"][-3:],
            "inner_monologue": mind["inner_monologue"],
        }
        return {"turn": {**state["turn"], "memory_context": memory}}

    return recall_memory


def make_supervisor_route(persona: PersonaVector) -> NodeFn:
    def supervisor_route(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "supervisor_route")
        mind = state["minds"][persona.agent_id]
        # Worker dialectique si clash émotionnel, sinon worker preuve.
        worker = "dialectic" if mind["arousal"] > 0.5 or state["turn"].get("persuasion", 0) > 0.6 else "evidence"
        return {"turn": {**state["turn"], "worker": worker}}

    return supervisor_route


def make_parallel_gather(persona: PersonaVector) -> NodeFn:
    """Simule un DAG parallèle : deux requêtes preuve fusionnées (LLMCompiler-inspired)."""

    def parallel_gather(state: ShowState, runtime: Runtime[ShowContext]) -> dict:
        _notify(runtime, persona, "parallel_gather")
        ctx = runtime.context
        if not ctx.enable_web_search or ctx.client is None:
            return {"turn": {**state["turn"], "evidence": ""}}
        claim = state["turn"].get("claim", state["topic"])
        queries = [
            f"données chiffrées récentes 2025 : {claim} ({persona.specialization})",
            f"coûts et impacts chiffrés 2025 : {state['topic']}",
        ]
        chunks = []
        for q in queries:
            result = llm.search(ctx.client, ctx.model_internal or SHOW_CONFIG["model_internal"], q)
            if result and not result.startswith("Erreur"):
                chunks.append(result)
        merged = "\n---\n".join(chunks)
        return {"turn": {**state["turn"], "evidence": merged, "evidence_query": " | ".join(queries)}}

    return parallel_gather


def route_supervisor(state: ShowState) -> str:
    return state["turn"].get("worker", "evidence")


def route_critic_gate(state: ShowState) -> str:
    return "voice" if state["turn"].get("critic_pass") else "revise_draft"
