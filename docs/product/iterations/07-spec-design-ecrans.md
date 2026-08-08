# Itération 7 — Spec design écran par écran

**Date :** 2026-07-14  
**Produit :** V.TV Le Conclave

---

## Écran 1 — Accueil spectateur (idle)

**État actuel :** `ui_preview_idle.png` — déjà sombre, professionnel.  
**Évolutions :**

- Titre : `V.TV` + sous-titre `LE CONCLAVE` (eyebrow, letterspacing)
- Bandeau : `EN ATTENTE DE SYNCHRONISATION` (pas « choisir un débat »)
- Sujet affiché comme **syscall pending** : `syscall: trust_ai_medical_diagnosis`
- Deux silhouettes invités en opacity 0.3, pulse idle
- CTA principal : `▶ LANCER LE DIRECT` (gold)
- CTA secondaire : `Injecter un paquet avant le boot` (oreillette pré-direct ✅)

**Son :** room tone -30 LUFS, clic studio sur hover bouton

---

## Écran 2 — Direct (live)

**État actuel :** `ui_preview_live.png` — structure 3 colonnes OK.

### Zone A — Masthead
```
[V.TV ● DIRECT]  round 2/5  │  SYSLOAD ████░░ 0.62  │  [RÉGIE]
```
- `SYSLOAD` = binding sur `state.tension`
- Badge DIRECT pulse 1Hz

### Zone B — Plateau
- **Invité A (gauche)** : silhouette blue, sous-titres karaoké, nom + rôle Conclave (`LE FLUX`)
- **Centre** : modérateur compact, VS logo subtil
- **Invité B (droite)** : silhouette coral
- **Plan caméra** : wide par défaut ; cut medium sur `currentSpeaker`
- **Pulse** : scale 1.0→1.05 sur RMS audio

### Zone C — Bas de page
```
┌─ INJECTION DE PAQUET ─────────────────────────────┐
│ [pseudo] [________________________________] [SEND] │
│ file: 2/3 en attente                              │
└───────────────────────────────────────────────────┘
```
- Réactions : `🔥 12  🤔 8  👏 24` (compteurs locaux)

### Overlays événementiels
| Event | Visuel | Son |
|-------|--------|-----|
| `moderator_interject` | Sting rouge 0.5s | Glass break soft |
| `evidence_used` | Carte source slide-in | Paper rustle |
| `earpiece` read | PACKET DELIVERED cyan | Modem chirp |
| concession | PATCH APPLIED | Git merge sound |
| conclusion | COMMIT FINAL | End sting |

---

## Écran 3 — Coulisses /proc (régie)

Toggle `RÉGIE` révèle panneau droit (existe : `backstageVisible`) :

```
/proc/show0
├── guest_a (Le Flux)
│   ├── stance: +0.72 → +0.58 (drift)
│   ├── conviction: 0.81
│   ├── last_thought: "Il esquive le coût humain..."
│   └── tactic: reframe
├── guest_b (Le Protocole)
│   └── ...
└── sysload: 0.62 [INTERJECT ARMED]
```

Police : `Consolas` (existe : `theme.mono`)

---

## Écran 4 — Post-show

- Timeline horizontale des tours (clic = replay texte + audio)
- **COMMIT FINAL** : résumé modérateur
- Export : JSON (existe) + `best_moments.json` (tours max tension)
- Bouton : `Rejouer` / `Nouveau syscall`

---

## Design tokens finaux

```qml
// Ajouts proposés à theme {}
readonly property color packet: "#00FFD1"
readonly property color mind: "#9B7AFF"
readonly property color sysloadLow: "#4DA3FF"
readonly property color sysloadHigh: "#FF6257"
```

---

## Review itération 7

**Amélioration :** spec visuelle complète, événements mappés au moteur.  
**Next :** comment présenter ce produit (pitch, démo, narrative).
