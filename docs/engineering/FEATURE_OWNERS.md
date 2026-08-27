# Feature ownership — branches cloud

Base : `master` après le commit foundation (carve ownership).
Les agents cloud n'éditent **que** leur arbre. Le compositeur
[`src/show/graph/show_graph.py`](../../src/show/graph/show_graph.py) est **figé** :
personne ne le réécrit sauf correctif de câblage explicitement demandé
(ex. nœud ``decide_after_update`` pour lire ``has_earpiece(context)``).

## Contrat `ShowState` / `MindState`

Seul `feat/shared-memory` peut modifier les TypedDict (champs **optionnels**
seulement, `total=False`). Les autres branches consomment le contrat :

| Rôle | Lit | Écrit |
|------|-----|-------|
| Invité | `transcript`, `minds`, `turn`, `pending_audience_question` | `minds[leur_id]`, `turn`, une entrée transcript |
| Animateur | `tension`, `stance_history`, transcript | `current_speaker`, `moderator_notes`, transcript, `pending_audience_question` |
| Moteur (`update_shared_state`) | minds, transcript round | `tension`, `stance_history`, minds (decay) |

## `feat/guests`

Owned:

- `src/show/guests/` (personas, nodes, subgraph, presets)
- shims `src/show/personas/`, `src/show/nodes/`, `src/show/graph/guest_subgraph.py`, `config/show_presets.py` (réexports seulement)

Interdit : `ShowState` / `MindState`, nœuds modérateur, QML, CI.

## `feat/moderator`

Owned:

- `src/show/host/` (persona Mr Bullshit, prompts, nœuds open/floor/interject/conclude)

Interdit : sous-graphe invité, algos `mind.py`, QML.

## `feat/shared-memory`

Owned:

- `src/show/memory/` (`state.py`, `mind.py`, `update.py`)
- `tests/test_show_mind.py`

Interdit : prompts invités, QML, nœuds host hors consommation du contrat.

## `eng/ui-platform`

Owned:

- `main.py`
- `src/backend_bridge.py`
- `src/ui/qml/`
- `tests/preview_ui.py`

API moteur : `run_show` + signaux / `emit`. Interdit : graphes LangGraph, `ShowState` schema.

## `eng/quality`

Owned:

- `.github/workflows/`
- `tests/` (organisation, pas de logique show hors tests)
- `scripts/` (benchmarks / viewers)

Interdit : logique show hors tests / scripts de mesure.

## `src/show/runtime/`

Partagé / figé : `context.py`, `llm.py`, `runner.py`.
`eng/ui-platform` consomme via `run_show` / `emit` / oreillette ; ne pas forker le runtime
sans ticket d'ownership.
