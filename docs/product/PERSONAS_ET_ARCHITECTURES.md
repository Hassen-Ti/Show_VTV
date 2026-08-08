# Personas, architectures agentiques & logique du show

**Date :** 2026-07-14

---

## Les questions qu'on se pose (et qu'on devrait toujours se poser)

| Question | Pourquoi c'est critique |
|----------|------------------------|
| **Qu'est-ce qu'un persona ici ?** | Éviter de confondre « prompt ChatGPT » et « agent avec état + graphe » |
| **Quelle architecture agentique pour quel caractère ?** | Le Flux (provocateur) n'a pas le même workflow que Le Protocole (diplomate) |
| **Le domaine pilote-t-il la cognition ou seulement le lexique ?** | Avant : domaine = séquence figée. Maintenant : domaine = nœuds de preuve/pensée, architecture = workflow |
| **Où vit l'état ?** | `ShowState` partagé — transcript, minds, tension, turn scratch |
| **Comment mesurer qu'une architecture est meilleure ?** | Benchmark agent : tactique valide, preuve, monologue, tension, qualité composite |
| **Est-ce publié / vérifiable ?** | Chaque architecture référence un paper ou pattern LangGraph documenté |

---

## Qu'est-ce qu'un persona ?

Un **persona** n'est pas un simple system prompt. C'est un **vecteur frozen** (`PersonaVector`) qui compose :

```
Persona = Identité + Caractère + Domaine + Architecture agentique
```

| Champ | Rôle | Exemple |
|-------|------|---------|
| `personality` | Émotions, tactiques, stubbornness | `provocateur` |
| `domain` | Lexique, style de preuve | `physicien` |
| `specialization` | Sujet d'expertise libre | `intelligence artificielle` |
| `architecture_id` | **Workflow LangGraph** | `react` |
| `cognitive_sequence` | Topologie résolue (arch × domaine) | `listen→verify_facts→hypothesize→strategize` |
| `initial_stance` / `conviction` | Opinion de départ | `+0.75` |
| `tactics` | Tactiques autorisées au plateau | `clash`, `moral_attack`… |

**Dans le Conclave V.TV :**
- `provocateur` = **Le Flux** → architecture `react`
- `diplomate` = **Le Protocole** → architecture `reflexion`
- `cerebral` = **L'Archive** → architecture `plan_execute`

---

## Comment la logique est faite

### Niveau show (orchestrateur)

```
START → moderator_open → allocate_floor
      → guest_a subgraph | guest_b subgraph
      → update_shared_state (tension, stance_history)
      → interject | allocate | conclude
```

### Niveau invité (sous-graphe — **architecture-driven**)

Chaque invité compile un graphe depuis `architecture_id` :

```
[architecture prefix] → strategize → (concede?) → draft
    → [post-draft: reflect | critic | self_correct] → voice → deliver
```

### Nœuds = fonctions pures + LLM

| Famille | Nœuds | Rôle |
|---------|-------|------|
| Perception | `listen`, `recall_memory` | Analyse adversaire, met à jour `mind` |
| Planification | `plan` | Plan-and-Execute / ReWOO |
| Preuve | `verify_facts`, `parallel_gather`… | Web search typée |
| Pensée | `hypothesize`, `reframe_concept`… | Raisonnement interne |
| Contrôle | `supervisor_route`, `critic_verify` | Routing / vérification |
| Stratégie | `strategize` | Choix tactique |
| Diffusion | `draft` → `voice` → `deliver` | Réplique antenne + monologue |

### État partagé (`ShowState`)

- **`minds[agent_id]`** : stance, conviction, arousal, beliefs, grudges, inner_monologue
- **`turn`** : scratch du tour (claim, evidence, angle, plan, reflection, critic_pass…)
- **`tension`** : SYSLOAD du plateau (émotions + densité d'attaques)

---

## 10 architectures agentiques (sources vérifiées)

| ID | Pattern | Source |
|----|---------|--------|
| `react` | ReAct | Yao et al., ICLR 2023 — [arxiv:2210.03629](https://arxiv.org/abs/2210.03629) |
| `reflexion` | Reflexion | Shinn et al., NeurIPS 2023 — [arxiv:2303.11366](https://arxiv.org/abs/2303.11366) |
| `plan_execute` | Plan-and-Execute | [LangGraph tutorial](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/) |
| `rewoo` | ReWOO | Xu et al., ACL 2023 — [arxiv:2305.18354](https://arxiv.org/abs/2305.18354) |
| `verifier_critic` | Verifier-Critic | [Digital Applied 2026 taxonomy](https://www.digitalapplied.com/blog/agent-architecture-patterns-taxonomy-2026) |
| `self_rag` | Self-RAG | Asai et al., ICLR 2024 — [arxiv:2310.11511](https://arxiv.org/abs/2310.11511) |
| `memory_augmented` | Memory-Augmented | [LangGraph memory concepts](https://langchain-ai.github.io/langgraph/concepts/memory/) |
| `supervisor_worker` | Supervisor-Worker | [LangGraph multi-agent](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/) |
| `parallel_dag` | Parallel DAG | Kim et al., LLMCompiler — [arxiv:2312.04511](https://arxiv.org/abs/2312.04511) |
| `correction_loop` | Self-Correction | [Inductivee patterns 2026](https://inductivee.com/blog/autonomous-agent-design-patterns) |

Fichier registre : `src/show/personas/architectures.py`

---

## Benchmark 1 persona × 10 architectures

**Persona fixe :** Provocateur physicien (IA, stance +0.75)  
**Adversaire :** Diplomate philosophe  
**Méthode :** 1 round LangGraph, LLM mocké personality-aware, scoring qualité

### Lancer

```bash
uv run python scripts/run_architecture_benchmark.py
uv run --with pytest python -m pytest tests/test_architecture_benchmark.py -v
```

### Dataframe

[`docs/product/architecture_benchmark.csv`](architecture_benchmark.csv)

Colonnes : `architecture_id`, `quality_score`, `steps_executed`, `tactic_used`, `has_plan`, `has_reflection`, `critic_pass`, `tension_final`, etc.

---

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `src/show/personas/vector.py` | Schéma PersonaVector |
| `src/show/personas/registry.py` | Personnalités × domaines × arch |
| `src/show/personas/architectures.py` | 10 patterns publiés |
| `src/show/graph/guest_subgraph.py` | Compile topologie par arch |
| `src/show/nodes/factories.py` | Nœuds cognitifs + arch nodes |
| `src/show/personas/benchmark_architectures.py` | Évaluation comparative |
