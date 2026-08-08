# Review 12 — Simulation latence & illusion du direct

**Date :** 2026-07-14  
**Hypothèse :** « TTS + LLM séquentiel = le spectateur quitte avant 2 min »

---

## Timeline simulée (show 3 rounds, pessimiste)

| Étape | Latence | Cumul |
|-------|---------|-------|
| Clic LANCER | 0s | 0s |
| `moderator_open` LLM | 3–8s | 8s |
| TTS ouverture (~150 car.) | 0.5s stream + 4s audio | 12s |
| Tour invité A (cognitive + deliver) | 8–15s | 27s |
| TTS invité A | 5s audio | 32s |
| Tour invité B | 8–15s | 47s |
| TTS invité B | 5s audio | 52s |
| **→ Fin round 1** | | **~52s** |
| Show complet (3 rounds) | × ~2.5 | **~4–6 min** |
| + recherche web (2×) | +10–20s | **~5–7 min** |

### Seuils attention (benchmarks implicites)

| Produit | Time-to-first-audio | Durée typique |
|---------|---------------------|---------------|
| VoxArena Live | ~90s débat court | 3–8 min |
| ChatGPT vocal | <1s | illimité |
| Podcast IA | 30s+ génération | 15–45 min |
| **VTV cible** | **<15s** | **5–10 min** |

---

## Simulation 3 scénarios

### A — TTS bloquant (spec v1.0)
- Attente silence entre tours pendant synthèse
- **Abandon estimé à 2 min :** 35% des spectateurs

### B — TTS pré-fetch (spec v1.1 proposée)
- Synthèse démarre dès `messageStream` à 50% du texte
- Audio précédent joue pendant LLM suivant
- **Abandon à 2 min :** 15%

### C — Texte-first, voix opt-in
- Flux texte immédiat (existant) + bouton 🔊
- **Abandon à 2 min :** 8%

---

## Verdict simulation

| Changement | Priorité |
|------------|----------|
| Queue audio + pré-fetch TTS | **P0** (confirmé, précisé) |
| Indicateur « buffering » discret | **P0** |
| Mode **texte-first** par défaut, voix activable | **P0 NEW** |
| `tts-1` pas `tts-1-hd` | confirmé |

**Score Conclave :** 9.3 → **9.2** si on n'ajoute pas texte-first ; **9.4** si on l'ajoute.
