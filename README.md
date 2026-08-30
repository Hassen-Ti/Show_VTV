# Show V.TV — débat IA (PyQt6 + QML)

Plateau TV simulé : deux invités agentiques (moteur LangGraph `src/show/`), modérateur, recherche web, interface QML (`ModernDebateInterface`).

## Installation (uv + `.venv/`)

Installer [uv](https://docs.astral.sh/uv/getting-started/), puis à la racine du dépôt :

```bash
uv sync
```

Copier `.env.example` vers `.env` et renseigner `OPENAI_API_KEY`.

## Lancer l'app

```bash
uv run python main.py
```

Show headless (CLI, sans UI) :

```bash
uv run python -m show.runner --topic "Faut-il ralentir l'IA ?" --rounds 3
```

## Arborescence utile

| Chemin | Rôle |
|--------|------|
| `main.py` | Point d'entrée UI |
| `src/show/` | Moteur show (graphe, personas, mind, LLM) |
| `src/backend_bridge.py` | Pont Qt ↔ moteur show |
| `src/config/show_config.py` | Modèle OpenAI, constantes du show |
| `src/show/guests/presets.py` | Présets d'invités pour l'UI |
| `src/ui/qml/` | Interface QML |
| `tests/` | Tests pytest + aperçu visuel |

## Tests

```bash
uv run --with pytest python -m pytest tests/ -q
uv run python tests/preview_ui.py   # screenshots dans docs/screenshots/ (sans clé API)
uv run python tests/test_web_search_openai.py
```

## Technique (résumé)

- Moteur : LangGraph, état partagé `ShowState` (transcript, minds, tension)
- LLM : `src/show/runtime/llm.py` (ChatOpenAI + recherche web Responses API)
- Config : `src/config/show_config.py` (`OPENAI_MODEL`, `max_rounds`, tokens)
