# Scripts — outils dev

## Avatars (optionnel)

Nécessite `uv sync --extra avatars` (Pillow, numpy) :

```bash
uv run python scripts/create_avatars.py
uv run python scripts/create_avatars.py --out-dir .
```

Les GIFs ne sont pas encore branchés dans l’UI QML.
