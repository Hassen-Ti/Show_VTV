# Étude produit V.TV Le Conclave (10 itérations)

- [x] Audit codebase + benchmark web (itérations 1–4)
- [x] Fusion vision « Conclave » + manifeste (itérations 5–6)
- [x] Spec design + GTM + roadmap (itérations 7–9)
- [x] Synthèse finale + `docs/product/VTV_PRODUCT_SPEC.md` (itération 10)

## Review produit

- Produit retenu : **V.TV Le Conclave** (score 9.6/10 après stress-test)
- 10 simulations : coût, latence, desktop, jargon, VoxArena, éducation, oreillette, /proc, fiabilité
- Changements v1.1 : progressive disclosure, texte-first, replay HTML P1.5, mode dégradé
- Prochaine implémentation : tension + coulisses lite + robustesse, puis TTS opt-in

---

# Architecture Lab — viewer traces

- [x] `TraceRecorder` + `ArchitectureTrace` (`src/show/personas/trace.py`)
- [x] Benchmark avec traces (`run_architecture_benchmark_with_traces`)
- [x] Viewer HTML `docs/product/architecture_lab.html` + `architecture_traces.json`
- [x] Tests pytest traces + génération HTML

## Review

- Ouvrir : `uv run python scripts/generate_architecture_viewer.py`
- Chaque nœud du graphe : **Input** (turn + mind + show) · **LLM** (system/user/response) · **Output** (delta)
- ShowState initial + final en bas ; filtre par agent (guest_a / guest_b)

---

# Mode spectateur + oreillette du modérateur

## Plan

- [x] Moteur : `has_earpiece` + `drain_earpiece` dans le graphe (ouverture + interjections)
- [x] Bridge : file thread-safe, `submitAudienceQuestion`, signaux Qt
- [x] UI : mode spectateur par défaut, champ « Poser une question au plateau », toggle Régie
- [x] Tests : smoke earpiece + preview mock + pytest vert (24 passed)

## Review

- Oreillette branchée sur l'infrastructure existante (`poll_earpiece` / `peek_earpiece` dans `ShowContext`).
- Question avant le direct : lue à l'ouverture par Mr Bullshit ; en direct : priorité dans `moderator_interject`.
- UI spectateur : régie masquée, coulisses off, bandeau PUBLIC + bouton RÉGIE discret en masthead.
- File max 3 questions ; signaux `audienceQuestionQueued` / `audienceQuestionRead` pour l'état visuel.

---

# Branches feature + agents cloud

## Plan

- [x] Promouvoir `feat/langgraph-debater-show-engine` → `master` distant
- [x] Commit foundation : `memory/` `host/` `guests/` `runtime/` + `FEATURE_OWNERS.md`
- [x] Pytest vert après carve (51 passed)
- [ ] Lancer 5 agents cloud (guests, moderator, shared-memory, ui-platform, quality)
- [ ] Rapport merge order

## Review

- Carve ownership : `src/show/{memory,host,guests,runtime}/` + compositeur figé `show_graph.py`
- Shims compat aux anciens chemins (`show.state`, `show.personas`, …)
- Ownership documenté dans `docs/engineering/FEATURE_OWNERS.md`
