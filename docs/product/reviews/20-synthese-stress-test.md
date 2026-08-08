# Review 20 — Synthèse : faut-il changer la recommandation ?

**Date :** 2026-07-14  
**Statut :** ✅ 10 reviews par simulation terminées

---

## Résumé des 10 hypothèses

| # | Hypothèse | Verdict | Change produit #1 ? |
|---|-----------|---------|---------------------|
| 11 | Coût/show abordable | ✅ ~$0.10 | Non — +compteur régie P1 |
| 12 | Latence tue l'engagement | ⚠️ | **Oui** — texte-first + pré-fetch TTS |
| 13 | Desktop seul = pas de scale | ⚠️ | **Oui** — replay HTML P1, web P1.5 |
| 14 | Jargon Conclave fait fuir | ⚠️ | **Oui** — progressive disclosure |
| 15 | VoxArena domine | ⚠️ | Non — différenciation mind/stance |
| 16 | Éducation = premier marché | 💡 | Non — dual GTM, preset classe P1 |
| 17 | Oreillette gadget | 💡 | Non — pilier mineur, feedback renforcé |
| 18 | /proc = vraie star | 💡 | Non — onglet coulisses lite P1 |
| 19 | Pannes API fréquentes | ⚠️ | **Oui** — mode dégradé P0 |
| 20 | Faut-il changer #1 ? | | **NON** |

---

## Décision finale après stress-test

### 🏆 Produit #1 inchangé : **V.TV Le Conclave**

**Score révisé :** 9.4 → **9.6/10** (mieux cadré, pas remplacé)

### Ce qui CHANGE dans la spec (v1.1)

| Zone | v1.0 | v1.1 |
|------|------|------|
| UX langage | Conclave partout | TV spectateur + Conclave régie |
| Audio | TTS obligatoire | **Texte-first**, voix opt-in |
| TTS | Fin de message | **Pré-fetch** à 50% stream |
| Distribution | Web Phase 3 | **Replay HTML P1**, viewer P1.5 |
| Coulisses | Régie only | **Onglet lite** spectateur |
| Robustesse | Non spec | **Mode dégradé** P0 |
| GTM | HN seul | **HN + éducation** |
| Oreillette | Feature majeure | Accent — feedback renforcé |

### Ce qui NE change PAS

- Vision philosophique (/dev/show0)
- Cast Flux / Protocole / Archive / Scheduler
- Moteur LangGraph + mind + tension
- MVP desktop comme cible dev
- Classement options (#1 Conclave)

### Classement révisé (option #7 éducation monte)

| # | Option | v1.0 | v1.1 |
|---|--------|------|------|
| 1 | V.TV Le Conclave | 9.4 | **9.6** |
| 2 | Plateau Minimaliste Cognitif | 8.0 | 8.3 |
| 3 | La Régie Invisible | 7.5 | 7.5 |
| 4 | Arène Multi-LLM | 7.0 | 7.0 |
| 5 | Studio Pédagogique | 6.0 | **7.2** |
| 6–10 | (autres) | — | inchangé |

---

## MVP Phase 1 révisé (priorités)

### P0 (semaines 1–3)
1. Jauge tension (« Tension du débat » spectateur / SYSLOAD régie)
2. Onglet coulisses lite (stance drift visible)
3. Mode dégradé (TTS fallback, LLM retry)
4. Feedback paquet lu amélioré

### P0 (semaines 3–5)
5. `show/tts.py` + pré-fetch + toggle voix
6. Silhouettes pulse (si voix on)
7. Sons studio légers

### P1 (semaines 6–8)
8. Export replay HTML
9. Preset « mode classe »
10. Compteur coût régie
11. Cartes d'argument sources

---

## Réponse philosophique — confirmée

Les simulations ne contredisent pas la métaphore. Elles imposent une règle :

> **Le Conclave est la vérité du système. La TV est l'interface humaine.**

Le monde dans l'ordi a besoin des deux couches — comme un OS a besoin du kernel ET du bureau.

---

📄 Spec mise à jour : `docs/product/VTV_PRODUCT_SPEC.md` v1.1
