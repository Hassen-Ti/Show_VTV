# Scripts — benchmarks & viewers

Outils de mesure / visualisation hors moteur show. Pas de clé API requise
(les benchmarks utilisent des mocks agentiques).

## Benchmarks

```bash
# 15 personas × métriques → docs/product/*.csv|json
uv run python scripts/run_persona_benchmark.py

# 10 architectures agentiques → docs/product/architecture_benchmark.*
uv run python scripts/run_architecture_benchmark.py
```

Options communes : `--out-dir PATH` (défaut `docs/product`).

## Viewers HTML

```bash
# Lab traces architectures (écrit HTML + JSON, ouvre le navigateur)
uv run python scripts/generate_architecture_viewer.py
uv run python scripts/generate_architecture_viewer.py --no-open

# Lab réflexion philosophe
uv run python scripts/generate_philosopher_viewer.py
uv run python scripts/generate_philosopher_viewer.py --no-open
```

## Avatars (optionnel)

Nécessite `uv sync --extra avatars` (Pillow, numpy) :

```bash
uv run python scripts/create_avatars.py
uv run python scripts/create_avatars.py --out-dir .
```
