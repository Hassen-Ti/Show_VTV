"""NODE_REGISTRY : nom de nœud cognitif → factory ``persona -> node_fn``."""

from show.nodes.delivery import make_deliver, make_draft, make_voice
from show.nodes.factories import (
    NodeFactory,
    NodeFn,
    STEP_LABELS,
    make_concede_then_refute,
    make_critic_verify,
    make_evidence_node,
    make_listen,
    make_parallel_gather,
    make_plan,
    make_recall_memory,
    make_reflect,
    make_revise_draft,
    make_self_correct,
    make_strategize,
    make_supervisor_route,
    make_think_node,
    route_critic_gate,
    route_supervisor,
)

NODE_REGISTRY: dict[str, NodeFactory] = {
    "listen": make_listen,
    # preuve (recherche web typée domaine)
    "verify_facts": make_evidence_node("verify_facts"),
    "recall_precedent": make_evidence_node("recall_precedent"),
    "quantify": make_evidence_node("quantify"),
    # pensée (raisonnement interne typé domaine)
    "hypothesize": make_think_node("hypothesize"),
    "build_analogy": make_think_node("build_analogy"),
    "reframe_concept": make_think_node("reframe_concept"),
    "find_contradiction": make_think_node("find_contradiction"),
    "recall_anecdote": make_think_node("recall_anecdote"),
    "narrative_frame": make_think_node("narrative_frame"),
    "model_tradeoff": make_think_node("model_tradeoff"),
    # architectures agentiques (patterns publiés)
    "plan": make_plan,
    "reflect": make_reflect,
    "revise_draft": make_revise_draft,
    "critic_verify": make_critic_verify,
    "self_correct": make_self_correct,
    "recall_memory": make_recall_memory,
    "supervisor_route": make_supervisor_route,
    "parallel_gather": make_parallel_gather,
    # stratégie et branche de caractère
    "strategize": make_strategize,
    "concede_then_refute": make_concede_then_refute,
    # mise en voix
    "draft": make_draft,
    "voice": make_voice,
    "deliver": make_deliver,
}

__all__ = ["NODE_REGISTRY", "NodeFactory", "NodeFn", "STEP_LABELS"]
