# Tasks

## 2026-07-02 — Moteur de show TV à personas agentiques

Plan : `docs/superpowers/specs/2026-07-02-show-persona-engine-design.md`

- [x] Spec de design (modules, algorithmes, diagrammes)
- [x] `PersonaVector` + validation stricte (`src/show/personas/vector.py`)
- [x] Registre 3 personnalités × 5 domaines + `make_guest` + `MODERATOR_PERSONA`
- [x] `ShowState` / `MindState` / `TranscriptEntry` avec reducer transcript
- [x] Algorithmes mind : dérive d'opinion, appraisal émotionnel, tension, concession
- [x] `NODE_REGISTRY` : listen, nœuds preuve/pensée par domaine, strategize, draft/voice/deliver
- [x] Sous-graphe invité dynamique (cognitive_sequence → topologie) + branche concession
- [x] Show graph : modérateur (open/allocate/interject/conclude), routage tension/rounds
- [x] Runner CLI headless + événements + export JSON
- [x] Tests : registre, mind purs, topologies, smoke show complet avec LLM mocké

### Review

- 20 nouveaux tests passent, 14 tests existants du pipeline débatteur inchangés et verts.
- Piège rencontré : un sous-graphe compilé renvoie l'état complet ; avec le reducer
  `operator.add` sur `transcript`, les entrées héritées du parent étaient dupliquées.
  Corrigé en enveloppant chaque sous-graphe (`_make_guest_node`) pour ne renvoyer que
  le delta (transcript ajouté, minds, turn).
- `src/agents/`, `backend_bridge.py` et l'UI QML non touchés (périmètre respecté).

## 2026-07-04 — Review & ship (pré-PR)

- [x] Revue complète du diff (2 subagents : `agents/react` + `src/show`)
- [x] Fix critique : contrat bridge ↔ `extract_turn_inputs` — le suffixe
  « en tenant compte de cet historique! » polluait `opponent_last`
- [x] Fix critique : `topic` stable passé du bridge au graphe (plus de blob historique)
- [x] Fix critique : agent one rounds 2+ reçoit la vraie réplique d'agent two
  au lieu de l'instruction générique
- [x] `debate_history` injecté dans le prompt de `draft_argument`
- [x] Runner show : `--rounds` validé, spec invité tolère les `:` dans la spécialisation
- [x] `test_web_search_openai.py` ne bloque plus pytest (skip si stdin non interactif)
- [x] `.gitignore` : `.pytest_cache/`, `/show_result.json`
- [x] Suite verte : 38 passed

### Review

- Restent en WARNING (non bloquants, notés pour plus tard) : streaming simulé après
  exécution du graphe (UX), température agent ignorée par le graphe, `llm.think` du show
  n'utilise pas le client injecté, recherche web quasi systématique en rebuttal
  (rhetoric `journalist`).
