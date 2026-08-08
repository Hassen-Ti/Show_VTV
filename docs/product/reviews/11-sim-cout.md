# Review 11 — Simulation coût par show

**Date :** 2026-07-14  
**Hypothèse :** « Un show de 3 rounds reste gratuit/abordable pour un usage hobby »

---

## Modèle de simulation

Basé sur `show_config.py` : `max_rounds: 3`, `internal_max_tokens: 160`, `delivery_max_tokens: 200`, `enable_web_search: True`.

### Estimation tours par show

| Phase | Appels LLM estimés | Tokens sortie | Recherche web |
|-------|-------------------|---------------|---------------|
| `moderator_open` | 1 | ~150 | non |
| Invité A × 3 rounds (cognitive seq ~4 nœuds + deliver) | ~12 | ~2 400 | 1–2 |
| Invité B × 3 rounds | ~12 | ~2 400 | 1–2 |
| `moderator_interject` (si tension > seuil, ~1×) | 1 | ~120 | non |
| `moderator_conclude` | 1 | ~150 | non |
| Nœuds internes (think/judge) | ~8 | ~1 200 | — |
| **Total** | **~35 appels** | **~6 500 tokens out** | **2–4 searches** |

### Coût monétaire (hypothèses marché 2026)

| Poste | Calcul | Coût/show |
|-------|--------|-----------|
| LLM (gpt-5.4-nano, ~$0.10/1M out) | 6 500 tok | ~$0.001 |
| LLM input (~20K tok) | | ~$0.002 |
| Web search (Responses API) | 3 × ~$0.01 | ~$0.03 |
| TTS (tts-1, ~2 500 car.) | 15 répliques × ~150 car. | ~$0.04 |
| **Total hobby** | | **~$0.07–0.12/show** |

### Scénario pessimiste (5 rounds, recherche agressive)

→ **~$0.25/show**, toujours acceptable pour démo.  
→ **Scénario prod intensive** (100 shows/jour) : **~$10–25/jour** — nécessite plafond.

---

## Verdict simulation

| Impact | Changement spec ? |
|--------|-------------------|
| Coût unitaire bas | ✅ Pas de pivot produit |
| Prod sans plafond = risque | ⚠️ **Ajout P1** : compteur coût en régie |
| Web search = poste principal | ⚠️ Toggle « recherche off » pour mode éco |

**Score Conclave :** 9.4 → **9.3** (léger ajustement ops, pas stratégique)
