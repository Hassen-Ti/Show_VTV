"""Registre des architectures agentiques — patterns publiés, mappés en topologies LangGraph.

Sources vérifiées :
- ReAct : Yao et al., « ReAct », ICLR 2023
- Reflexion : Shinn et al., « Reflexion », NeurIPS 2023
- Plan-and-Execute : LangChain / LangGraph prebuilt pattern
- ReWOO : Xu et al., « ReWOO », ACL 2023
- Verifier-Critic : taxonomy Digital Applied 2026
- Self-RAG : Asai et al., « Self-RAG », ICLR 2024
- Supervisor-Worker : LangGraph multi-agent subgraph pattern
- Parallel DAG : Kim et al., « LLMCompiler », 2024
- Correction loop : self-correction pattern (Inductivee / LangChain 2026)
- Memory-augmented : episodic memory pattern (MemGPT / agent memory surveys)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PostDraftMode = Literal["none", "reflect", "self_correct", "critic_gate"]


@dataclass(frozen=True)
class ArchitectureSpec:
    id: str
    name: str
    source: str
    reference: str
    description: str
    cognitive_path: tuple[str, ...]
    post_draft: PostDraftMode = "none"
    uses_supervisor: bool = False
    uses_memory_first: bool = False
    uses_plan_first: bool = False


# Nœuds cognitifs disponibles (préfixe avant strategize).
ARCHITECTURES: dict[str, ArchitectureSpec] = {
    "react": ArchitectureSpec(
        id="react",
        name="ReAct",
        source="Yao et al., ICLR 2023",
        reference="https://arxiv.org/abs/2210.03629",
        description="Raisonner (listen) → Agir (verify_facts) → Raisonner (hypothesize) → Décider.",
        cognitive_path=("listen", "verify_facts", "hypothesize"),
    ),
    "reflexion": ArchitectureSpec(
        id="reflexion",
        name="Reflexion",
        source="Shinn et al., NeurIPS 2023",
        reference="https://arxiv.org/abs/2303.11366",
        description="Pipeline cognitif classique + boucle réflexive post-brouillon avant diffusion.",
        cognitive_path=("listen", "verify_facts", "hypothesize"),
        post_draft="reflect",
    ),
    "plan_execute": ArchitectureSpec(
        id="plan_execute",
        name="Plan-and-Execute",
        source="LangChain / LangGraph pattern",
        reference="https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/",
        description="Plan explicite du tour avant exécution des outils (preuve) et raisonnement.",
        cognitive_path=("listen", "plan", "verify_facts", "hypothesize"),
        uses_plan_first=True,
    ),
    "rewoo": ArchitectureSpec(
        id="rewoo",
        name="ReWOO",
        source="Xu et al., ACL 2023",
        reference="https://arxiv.org/abs/2305.18354",
        description="Écoute minimale puis plan ; workers exécutent sans re-planifier à chaque pas.",
        cognitive_path=("listen", "plan", "verify_facts", "hypothesize"),
        uses_plan_first=True,
    ),
    "verifier_critic": ArchitectureSpec(
        id="verifier_critic",
        name="Verifier-Critic",
        source="Digital Applied taxonomy 2026",
        reference="https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026",
        description="Génération d'angle puis vérification critique avant choix tactique.",
        cognitive_path=("listen", "verify_facts", "hypothesize", "critic_verify"),
    ),
    "self_rag": ArchitectureSpec(
        id="self_rag",
        name="Self-RAG",
        source="Asai et al., ICLR 2024",
        reference="https://arxiv.org/abs/2310.11511",
        description="Retrieve → raisonner → brouillon → auto-critique → révision conditionnelle.",
        cognitive_path=("listen", "verify_facts", "hypothesize"),
        post_draft="critic_gate",
    ),
    "memory_augmented": ArchitectureSpec(
        id="memory_augmented",
        name="Memory-Augmented",
        source="Episodic memory pattern (agent surveys 2024–2026)",
        reference="https://langchain-ai.github.io/langgraph/concepts/memory/",
        description="Rappel des croyances/grudges avant perception de l'adversaire.",
        cognitive_path=("recall_memory", "listen", "verify_facts", "hypothesize"),
        uses_memory_first=True,
    ),
    "supervisor_worker": ArchitectureSpec(
        id="supervisor_worker",
        name="Supervisor-Worker",
        source="LangGraph multi-agent subgraph",
        reference="https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/",
        description="Superviseur route vers worker preuve (empirique) ou dialectique selon le clash.",
        cognitive_path=("listen", "supervisor_route"),
        uses_supervisor=True,
    ),
    "parallel_dag": ArchitectureSpec(
        id="parallel_dag",
        name="Parallel DAG (LLMCompiler)",
        source="Kim et al., 2024",
        reference="https://arxiv.org/abs/2312.04511",
        description="Collecte parallèle de preuves (faits + quantification) puis synthèse.",
        cognitive_path=("listen", "parallel_gather", "hypothesize"),
    ),
    "correction_loop": ArchitectureSpec(
        id="correction_loop",
        name="Self-Correction",
        source="LangChain / Inductivee 2026",
        reference="https://inductivee.com/blog/autonomous-agent-design-patterns",
        description="Brouillon puis passe de correction avant mise en voix.",
        cognitive_path=("listen", "verify_facts", "hypothesize"),
        post_draft="self_correct",
    ),
}

ARCHITECTURE_IDS = tuple(ARCHITECTURES.keys())

# Meilleure architecture par personnalité (assignée après benchmark).
PERSONALITY_ARCHITECTURE: dict[str, str] = {
    "provocateur": "react",
    "diplomate": "reflexion",
    "cerebral": "plan_execute",
}


def get_architecture(architecture_id: str) -> ArchitectureSpec:
    if architecture_id not in ARCHITECTURES:
        raise ValueError(
            f"architecture inconnue: {architecture_id!r} (choix: {sorted(ARCHITECTURES)})"
        )
    return ARCHITECTURES[architecture_id]


def cognitive_sequence_for(architecture_id: str) -> tuple[str, ...]:
    """Séquence nominale (nœuds génériques — résolus par domaine dans le registre)."""
    spec = get_architecture(architecture_id)
    path = list(spec.cognitive_path)
    if spec.uses_supervisor:
        return ("listen", "supervisor_route", "strategize")
    if "strategize" not in path:
        path.append("strategize")
    return tuple(path)
