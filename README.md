# Show V.TV — débat IA (PyQt6 + QML)

Application PyQt6 avec deux agents GPT qui débattent, recherche web et interface QML (`ModernDebateInterface`).

## Installation

```bash
pip install -r requirements.txt
```

Copier `.env.example` vers `.env` et renseigner `OPENAI_API_KEY`.

## Lancer l’app

```bash
python main.py
```

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
python tests/test_factcheck.py
python tests/test_web_search_openai.py
python tests/test_miniscreen.py
```

## Technique (résumé)

- Modèle OpenAI avec appels outils / streaming selon les agents  
- Recherche web : DuckDuckGo côté utils (`src/utils/web_search_tool.py`)  
- Températures et limites de tokens configurées dans `src/config/settings.py`
