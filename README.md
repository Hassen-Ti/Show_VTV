# Show V.TV — débat IA (PyQt6 + QML)

Application PyQt6 avec deux agents GPT qui débattent, recherche web et interface QML (`ModernDebateInterface`).

## Installation (uv + `.venv/`)

Installer [uv](https://docs.astral.sh/uv/getting-started/), puis à la racine du dépôt (le dossier qui contient `pyproject.toml` et `uv.lock`) :

```bash
uv sync
```

Éviter `pip install` global : les dépendances sont gérées par `pyproject.toml` et le venv créé sous `.venv/`.

Extras optionnels :

- LangGraph + export JPG du graphe — `uv sync --extra langgraph-example`
- `scripts/create_avatars.py` — `uv sync --extra avatars`

Les deux : `uv sync --extra langgraph-example --extra avatars`

Copier `.env.example` vers `.env` et renseigner `OPENAI_API_KEY`.

## Lancer l’app

`uv run` utilise le venv du projet (`.venv/`).

```bash
uv run python main.py
```

Si tu préfères activer le venv à la main : sous Windows PowerShell, `.venv\Scripts\Activate.ps1` puis `python main.py`.

Le code applicatif vit sous `src/` (agents, config, QML, pont `backend_bridge.py`).

## Arborescence utile

| Chemin | Rôle |
|--------|------|
| `main.py` | Point d’entrée unique |
| `src/agents/` | Agents, modérateur, fact-checker |
| `src/config/` | Prompts, personas, topics |
| `src/ui/qml/` | Interfaces QML |
| `src/ui/assets/` | Images / GIF avatars |
| `tests/` | Scripts de test manuels |
| `scripts/create_avatars.py` | Génération d’avatars (nécessite `pillow`, `numpy`) |
| `docs/notes/` | Brouillons / idées (textes) |

## Tests manuels

```bash
uv run python tests/test_factcheck.py
uv run python tests/test_web_search_openai.py
uv run python tests/test_miniscreen.py
```

## Technique (résumé)

- Modèle OpenAI avec appels outils / streaming selon les agents  
- Recherche web : Responses API / prompt enrichi (`src/agents/base_agent.py`)  
- Températures et limites de tokens configurées dans `src/config/settings.py`
