# Review 13 — Simulation adoption : desktop PyQt seul

**Date :** 2026-07-14  
**Hypothèse :** « 95% des spectateurs potentiels ne téléchargeront jamais une app desktop »

---

## Funnel simulé (1000 visiteurs GitHub/HN)

| Étape | Taux | Restants |
|-------|------|----------|
| Voient la démo vidéo | 100% | 1000 |
| Cliquent le repo | 12% | 120 |
| Installent `uv sync` + `.env` | 25% | 30 |
| Lancent un show complet | 60% | 18 |
| Reviennent J+7 | 20% | **3.6** |

**Retention J+7 : 0.36%** — typique outil dev desktop sans distribution.

### Comparaison

| Canal | Funnel J+7 estimé |
|-------|-------------------|
| Desktop PyQt (actuel) | 0.3–0.5% |
| Web viewer (Phase 3) | 2–5% |
| Embed iframe article | 8–15% (lecteurs engagés) |
| Twitch 24/7 (spin-off) | 0.1% install, 5% watch |

---

## Verdict simulation

Le Conclave comme **vision** tient. Le **canal desktop seul** ne tient pas pour scale.

| Changement spec | Priorité |
|---------------|----------|
| MVP reste desktop (OK — moteur) | P0 |
| **Headless + export HTML replay** remonte en **P1** (pas P2) | ⬆️ |
| **Viewer web read-only** en P1.5 (WebSocket transcript) | ⬆️ |
| Pitch HN = démo vidéo + replay link, pas « installez » | GTM |

**Score Conclave :** inchangé 9.4 — mais **roadmap réordonnée**.
