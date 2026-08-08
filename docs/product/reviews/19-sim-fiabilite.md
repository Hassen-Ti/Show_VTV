# Review 19 — Simulation fiabilité & mode dégradé

**Date :** 2026-07-14  
**Hypothèse :** « API OpenAI down 2% du temps → show cassé = confiance détruite »

---

## Scénarios de panne (1000 shows simulés)

| Panne | Fréquence | Impact actuel | Impact avec dégradé |
|-------|-----------|---------------|---------------------|
| LLM timeout (>20s) | 1.5% | Crash/error | Retry 1× → texte fallback |
| TTS échec | 2% | Silence | Texte seul auto |
| Web search fail | 4% | Tour sans sources | Badge « hors ligne » |
| Rate limit 429 | 0.8% | Stop | Queue + backoff |
| Clé API absente | 15% (dev) | Crash | Mode mock (existe partiellement) |

---

## Spec mode dégradé proposée

```
Niveau 0 — Full : LLM + search + TTS
Niveau 1 — Voix off : LLM + search, pas TTS
Niveau 2 — Offline : LLM seul, mock search
Niveau 3 — Preview : transcript mock (tests/preview_ui.py ✅)
```

---

## Verdict simulation

| Changement | Priorité |
|------------|----------|
| Graceful TTS fallback | **P0 NEW** |
| Retry LLM 1× avec timeout 20s | **P0 NEW** |
| Indicateur niveau dégradé en masthead | P1 |
| Mode mock sans clé en UI | P1 (améliorer message actuel) |

**Pas de changement vision** — robustesse ops ajoutée au MVP.
