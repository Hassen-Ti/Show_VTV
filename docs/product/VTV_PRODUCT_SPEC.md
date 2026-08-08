# V.TV Le Conclave — Spécification Produit

**Version :** 1.1 (stress-test 10 simulations)  
**Date :** 2026-07-14  
**Auteur :** Product AI Owner (étude 10 itérations + 10 reviews simulées)  
**Statut :** Recommandation confirmée après stress-test

---

## Résumé exécutif

**V.TV Le Conclave** transforme Show V.TV d'un simulateur de débat textuel en **plateau TV natif internet** — le lieu où les processus du monde numérique s'affrontent en direct, sous les yeux de peers qui injectent des paquets dans le flux.

**Tagline :** *Le monde se débat en direct.*

**Score produit :** 9.4 → **9.6/10** après 10 simulations (produit #1 confirmé, exécution affinée).

**Règle UX v1.1 :** *Le Conclave est la vérité du système. La TV est l'interface humaine.* (progressive disclosure)

**Prochaine étape :** Phase 1 MVP révisé — tension visible, coulisses lite, mode dégradé, puis TTS opt-in.

---

## 1. Vision

### 1.1 Le problème

Le débat en ligne est soit :
- un **fil infini** sans tour de parole (Twitter, Reddit)
- un **chatbot 1:1** sans tension ni spectacle
- une **vidéo générée** sans interaction live

Il manque un **espace partagé** où des positions s'affrontent *en temps réel*, visiblement, avec des témoins qui peuvent intervenir.

### 1.2 La solution

Un plateau TV simulé où :
- 2 agents-processus débattent via LangGraph
- 1 modérateur-scheduler gère le temps et la tension
- le public injecte des paquets (oreillette)
- la SYSLOAD montre la charge argumentative
- les coulisses révèlent `/proc/show0` (mind states)

### 1.3 Ce qui existe déjà (assets)

| Asset | Fichier | Maturité |
|-------|---------|----------|
| Moteur LangGraph | `src/show/graph/show_graph.py` | ✅ |
| Personas vectorisées | `src/show/personas/` | ✅ |
| Mind + tension | `src/show/mind.py` | ✅ |
| Oreillette spectateur | `src/backend_bridge.py` | ✅ |
| UI studio QML | `src/ui/qml/ModernDebateInterface.qml` | ✅ |
| Mode spectateur/régie | QML `spectatorMode`, `regieVisible` | ✅ |
| Presets sujets | `src/config/show_presets.py` | ✅ |
| Tests | 24 passed | ✅ |

### 1.4 Ce qui manque pour « illuminer »

| Gap | Priorité |
|-----|----------|
| Voix TTS | P0 |
| Jauge SYSLOAD visible | P0 |
| Embodiment (silhouettes + pulse) | P0 |
| Sons studio | P0 |
| Langage Conclave (UX copy) | P0 |
| Cartes d'argument / sources | P1 |
| Replay timeline | P1 |
| Mémoire inter-épisodes | P1 |
| Viewer web / stream | P2 |

---

## 2. Philosophie — Le monde dans l'ordinateur

### 2.1 Que serait un plateau TV virtuel ?

Un **point de terminaison de consensus** — l'interface publique (`/dev/show0`) où des flux hétérogènes sont forcés de se synchroniser devant des témoins.

| Métaphore TV | Équivalent numérique |
|--------------|---------------------|
| Studio | Sandbox d'exécution isolée |
| Direct | Session live non-bloquante |
| Antenne | Stream / publication |
| Oreillette | Buffer d'injection réseau |
| Régie | Root access /proc |
| Générique | Boot sequence |
| Conclusion | Commit snapshot (pas vérité absolue) |

Le plateau est le **seul endroit du monde numérique où la lenteur est imposée** : on ne scroll pas, on écoute l'adversaire.

### 2.2 Que seraient ces agents ?

Des **ambassadeurs de stratégies computationnelles**, pas des humains simulés :

```
Agent = PersonaVector + MindState + Topologie cognitive
      = politique d'interprétation du monde
```

| Propriété | Signification |
|-----------|---------------|
| `cognitive_sequence` | Pipeline de traitement |
| `initial_stance` | Prior sur le sujet |
| `stubbornness` | Résistance au gradient social |
| `concession_rate` | Taux de merge intellectuel |
| `mind.inner_monologue` | Logs privés avant parole publique |
| `stance_history` | Commit log de positions |

**Cast Conclave :**

| Persona code | Identité | Archétype réseau |
|--------------|----------|------------------|
| `provocateur` | **Le Flux** | Viralité, hot takes |
| `diplomate` | **Le Protocole** | Consensus, modération |
| `cerebral` | **L'Archive** | Profondeur, sources |
| Mr Bullshit | **Le Scheduler** | Allocation temps, tension |

---

## 3. Fonctionnalités

### 3.1 MVP Phase 1 révisé (4–6 semaines)

> Affiné après simulations coût, latence, adoption, jargon, concurrence (reviews 11–20).

#### P0 — Semaines 1–3 (sans TTS)

| ID | Feature | Détail |
|----|---------|--------|
| F1 | Jauge tension | « Tension du débat » (spectateur) / SYSLOAD (régie) |
| F2 | Coulisses lite | Onglet spectateur : stance + drift visible ; /proc complet en régie |
| F3 | Mode dégradé | TTS fallback texte ; LLM retry 1× timeout 20s ; badge hors-ligne si search fail |
| F4 | Feedback paquet | Toast « Votre question est à l'antenne » ; pseudo optionnel |
| F5 | Langage progressif | TV en surface ; Conclave en régie uniquement |

#### P0 — Semaines 3–5 (voix opt-in)

| ID | Feature | Détail |
|----|---------|--------|
| F6 | TTS opt-in | **Texte-first par défaut** ; toggle 🔊 Voix |
| F7 | Pré-fetch TTS | Synthèse à 50% du stream ; queue audio |
| F8 | Embodiment | Silhouettes + pulse si voix active |
| F9 | Sons studio | Room tone, stings (interjection, paquet, conclusion) |

#### F10 — Overlay sources (P0 fin)
- Carte source basique quand `evidence_used`

#### Mode dégradé (nouveau P0)

```
Niveau 0 — Full : LLM + search + TTS
Niveau 1 — Voix off : LLM + search, pas TTS
Niveau 2 — Offline : LLM seul
Niveau 3 — Preview : mock (tests/preview_ui.py)
```

### 3.2 Phase 1.5 (6–8 semaines)

- Export **replay HTML** (partageable, corrige funnel desktop)
- Preset **mode classe** (jargon off, coulisses simplifiées)
- Compteur coût en régie (~$0.10/show)
- Cartes d'argument complètes
- Viewer web read-only (WebSocket transcript)

### 3.3 Phase 2 (8–12 semaines)

- Cartes d'argument complètes
- Novelty gate (anti-répétition sémantique)
- Timeline replay post-show
- Persistance `stance_history` (SQLite)
- Ingestion sujet tendance
- Export best moments
- Badge multi-LLM en régie

### 3.4 Phase 3 (16+ semaines)

- Viewer web (WebSocket)
- Stream Twitch/YouTube
- Peers authentifiés
- Chambre 3D légère
- Widget embed presse
- Kernels (saisons)

---

## 4. Design

### 4.1 Design tokens (ajouts)

```qml
readonly property color packet: "#00FFD1"    // injection spectateur
readonly property color mind: "#9B7AFF"     // coulisses /proc
readonly property color sysloadLow: "#4DA3FF"
readonly property color sysloadHigh: "#FF6257"
```

### 4.2 Layout direct (progressive disclosure)

**Couche spectateur (TV) :**
```
┌─────────────────────────────────────────────────────────┐
│ V.TV ● DIRECT │ round 2/5 │ TENSION ████░░ 0.62 │ RÉGIE│
├─────────────────────────────────────────────────────────┤
│  [INVITÉ A]              [MODÉRATEUR]      [INVITÉ B]   │
│  sous-titres               centre            sous-titres │
├─────────────────────────────────────────────────────────┤
│ [Coulisses ▾] stance A: +0.58 ↓0.14  │  B: -0.71      │
├─────────────────────────────────────────────────────────┤
│ Poser une question au plateau  [pseudo] [____] [ENVOYER]│
│ 🔊 Voix off                    🔥 12  🤔 8  👏 24        │
└─────────────────────────────────────────────────────────┘
```

**Couche régie (Conclave) :** SYSLOAD, /proc/show0, « Injecter un paquet », PACKET DELIVERED, COMMIT FINAL.

### 4.3 Événements visuels

| Event moteur | Overlay | Son |
|--------------|---------|-----|
| `moderator_interject` | Sting rouge | Glass break |
| `earpiece` read | PACKET DELIVERED | Modem chirp |
| concession (mind) | PATCH APPLIED | Merge |
| `evidence_used` | Carte source | Paper |
| conclude | COMMIT FINAL | End sting |

### 4.4 Mode /proc (régie)

Panneau monospace affichant par agent :
- stance actuelle + drift
- conviction
- dernière pensée interne
- tactic courante
- SYSLOAD + état interject

---

## 5. Parcours utilisateur

### 5.1 Peer (spectateur)

1. Arrive → mode spectateur (défaut)
2. Choisit preset ou syscall custom
3. (Optionnel) Injecte paquet pré-boot
4. Lance le direct → audio + visuel
5. Observe clash, SYSLOAD monte
6. Injecte paquet mid-show
7. Voit PACKET DELIVERED quand lu
8. Assiste au COMMIT FINAL
9. (V2) Replay best moments

### 5.2 Root (régie)

1. Toggle RÉGIE
2. Voit /proc/show0 en direct
3. Configure preset, rounds, sujet
4. (V2) Choisit modèles par agent

---

## 6. Architecture technique

```
QML (ModernDebateInterface)
    │ signaux Qt
    ▼
backend_bridge.ShowWorker
    │ oreillette queue (max 3)
    │ audio queue (new)
    ▼
show.graph.run_show (LangGraph)
    │ ShowState { tension, minds, transcript }
    ▼
show.llm + show.tts (new)
```

### 6.1 Nouveau module `show/tts.py`

```python
@dataclass
class VoiceProfile:
    speaker_id: str
    voice: str
    rate: float  # lié à arousal_gain

def synthesize(text: str, profile: VoiceProfile) -> bytes: ...
def prosody_from_persona(persona: PersonaVector) -> VoiceProfile: ...
```

### 6.2 Mapping voix

| Rôle | Voice OpenAI | Rate |
|------|--------------|------|
| Le Flux | nova | 1.15 |
| Le Protocole | alloy | 0.95 |
| L'Archive | onyx | 0.85 |
| Le Scheduler | echo | 1.0 |

---

## 7. Les 10 options — classement après stress-test (v1.1)

| # | Option | v1.0 | v1.1 | Décision |
|---|--------|------|------|----------|
| 1 | **V.TV Le Conclave** | 9.4 | **9.6** | ✅ Confirmé |
| 2 | Plateau Minimaliste Cognitif | 8.0 | 8.3 | Coulisses lite P1 |
| 3 | La Régie Invisible | 7.5 | 7.5 | Mode existant |
| 4 | Arène Multi-LLM | 7.0 | 7.0 | Phase 2 |
| 5 | Studio Pédagogique | 6.0 | **7.2** | GTM canal #2 |
| 6 | Symposium Distribué | 6.5 | 6.5 | Phase 3 |
| 7 | Émission 24/7 | 6.2 | 6.2 | Spin-off |
| 8 | Pipeline Showrunner | 5.8 | 5.8 | Export vidéo |
| 9 | Widget Embed | 5.5 | 5.5 | Phase 3 |
| 10 | Spectateur Vivant seul | — | — | Fusionné |

---

## 8. Benchmark concurrentiel

| Projet | URL | Ce qu'on retient |
|--------|-----|----------------|
| JedAI Council | jedaicouncil.com | Chambre 3D, cast divers |
| VoxArena | voxarena.ai | Pipeline 7 étapes, TTS prosodie |
| Symposium | github.com/imagineering-cc/symposium | DNA persona, distribué |
| Showrunner | github.com/divi-vijayakumar/Showrunner | Continuité cast/set |
| AITV.GG | aitv.gg | Spectateur co-créateur |
| AI Podcast Studio | github.com/mohamdImran/ai-podcast-studio | Q&A injectée audio |
| debate-agents | github.com/mmaazkhanhere/debate-agents | Cartes d'argument |

**Différenciation VTV :** seul produit combinant **mind state visible** + **oreillette** + **tension SYSLOAD** + **métaphore native internet**.

---

## 9. Go-to-market

### Pitch 30s

> Le monde numérique n'a pas de lieu pour se disputer. V.TV Le Conclave est le premier plateau natif internet : des processus s'affrontent en direct, et vous injectez vos paquets dans le flux. Ce n'est pas un chatbot. C'est /dev/show0.

### Démo 3 min

Boot → clash TTS → injection paquet → interjection → /proc → commit

**Différenciation VTV vs VoxArena :** open source, mind/stance visible, local/privacy, debugger du débat — pas course au multi-LLM.

---

## 9. Go-to-market (dual canal)

### Pitch 30s

> Le monde numérique n'a pas de lieu pour se disputer. V.TV Le Conclave est le premier plateau natif internet : des processus s'affrontent en direct, et vous voyez leurs opinions bouger en temps réel. Ce n'est pas un chatbot. C'est /dev/show0.

### Canaux

| Canal | Message | Format démo |
|-------|---------|-------------|
| HN / GitHub | « LangGraph as live TV — open source » | Vidéo + replay HTML |
| Éducation | « Voir penser un débat » | Preset mode classe + coulisses |
| Twitch (V3) | Spin-off 24/7 | Séparé |

---

## 10. Métriques de succès

| Métrique | MVP | Phase 2 |
|----------|-----|---------|
| Temps avant « wow » | &lt;30s | &lt;10s |
| Durée session moyenne | &gt;5 min | &gt;15 min |
| Paquets injectés / show | &gt;1 | &gt;3 |
| Taux fin de show | &gt;60% | &gt;80% |
| Tests passent | 24+ | 30+ |

---

## 11. Fichiers d'étude

- Itérations initiales : `docs/product/iterations/01` à `10`
- Stress-test simulations : `docs/product/reviews/11` à `20`

---

## 12. Décision (confirmée v1.1)

**Construire V.TV Le Conclave — Phase 1 MVP révisé.**

Priorités immédiates :
1. Jauge tension + coulisses lite (stance drift)
2. Mode dégradé (retry LLM, fallback TTS)
3. Feedback paquet amélioré
4. Puis TTS opt-in + pré-fetch

*Le monde se débat en direct.*
