# Itération 3 — Parcours spectateur & design studio numérique

**Date :** 2026-07-14  
**Input :** itération 2 + analyse `ModernDebateInterface.qml`

---

## Parcours spectateur cible (60 secondes → 30 minutes)

### T+0s — Arrivée (mode spectateur par défaut ✅)
- Écran « DIRECT » avec sujet du jour, noms invités, jauge tension à 0
- **Manque :** bruitage studio faible (room tone), pas de générique

### T+10s — Ouverture modérateur
- Mr Bullshit pose l'enjeu ; si question oreillette en file → mention à l'antenne ✅
- **Manque :** voix TTS ; sous-titres karaoké ; plan caméra (wide → modérateur)

### T+30s–5min — Clash
- Alternance invités, highlight speaker actif ✅ (`currentSpeaker`)
- Coulisses off en spectateur ✅
- **Manque :** réactions live (👏🔥🤔), carte d'argument avec sources, replay 10s

### T+5min — Interjection
- Modérateur coupe quand tension haute ✅ (`moderator_interject`)
- **Manque :** effet visuel « BREAKING », son de sting

### T+15min — Question spectateur lue
- Oreillette drain → modérateur ou invité ✅
- **Manque :** notification push « VOTRE QUESTION EST À L'ANTENNE », badge pseudo

### T+30min — Conclusion
- Modérateur conclut ✅
- **Manque :** verdict (pas de scoring), clip auto « meilleur moment », export

---

## Design system proposé : « Studio Numérique »

Extension des tokens existants (`theme.blue`, `theme.coral`, `theme.gold`) :

| Token | Usage | Valeur proposée |
|-------|-------|-----------------|
| `signal.live` | Badge DIRECT | `#FF2E44` (existe) |
| `signal.packet` | Question spectateur | `#00FFD1` cyan réseau |
| `signal.mind` | Coulisses / pensée | `#9B7AFF` violet process |
| `signal.tension` | Jauge clash | gradient coral→gold |
| `motion.cut` | Transition plan | 180ms hard cut (pas de fondu TV) |
| `sound.room` | Ambiance | -24 LUFS loop |

### Layout « 3 plans »

```
┌─────────────────────────────────────────────────┐
│  DIRECT ●  │  SUJET  │  TENSION ████░░  │ RÉGIE│
├─────────────────────────────────────────────────┤
│                                                 │
│   [INVITÉ A]          VS          [INVITÉ B]    │
│   avatar zone                   avatar zone     │
│   sous-titres                   sous-titres     │
│                                                 │
│              ┌──────────────┐                   │
│              │ MODÉRATEUR   │                   │
│              └──────────────┘                   │
├─────────────────────────────────────────────────┤
│  💬 Poser une question au plateau    [ENVOYER]  │
└─────────────────────────────────────────────────┘
```

### Embodiment minimal (phase 1)
- Pas de vidéo générative — **silhouettes lumineuses** pulsant avec la parole (audio RMS)
- Couleur = camp (blue/coral) ; taille = `arousal` du mind state
- **Coulisses** = panneau latéral révélant `stance`, `conviction`, dernière pensée interne

---

## Impact sur le classement (v3)

| Rang | Option | Note |
|------|--------|------|
| 1 | **VTV Spectateur Vivant** | ↑ Devient #1 : design system réalisable sur QML existant |
| 2 | **Le Conclave Numérique** | ↓ Identity layer vient après le vivant |
| 3 | **Plateau Minimaliste Cognitif** | — Coulisses comme feature premium |

**Insight :** illuminer d'abord (voix + lumière + tension), puis métaphoriser (agents = entités réseau).

---

## Review itération 3

**Amélioration :** parcours minute par minute, tokens design, embodiment cheap.  
**Manque :** specs fonctionnelles numérotées, priorisation MVP.  
**Next :** backlog MVP vs V2 avec effort estimé.
