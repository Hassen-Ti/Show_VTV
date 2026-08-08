# Itération 4 — Backlog MVP & architecture fonctionnelle

**Date :** 2026-07-14  
**Input :** itération 3 + analyse `backend_bridge.py`, `show/mind.py`

---

## MVP « Allumer le plateau » (4–6 semaines)

### P0 — Le show devient audible
| ID | Feature | Fichiers touchés | Effort |
|----|---------|------------------|--------|
| F1 | TTS par speaker (OpenAI/ElevenLabs) | `backend_bridge.py`, nouveau `show/tts.py` | M |
| F2 | Stream audio synchro avec `messageStream` | `ShowWorker` | M |
| F3 | Room tone + sting ouverture/clash | QML `SoundEffect` | S |

### P0 — Le show devient visible
| ID | Feature | Fichiers touchés | Effort |
|----|---------|------------------|--------|
| F4 | Jauge tension temps réel (`tension` dans state) | QML binding | S |
| F5 | Pulse avatar lié à RMS audio | QML Canvas | M |
| F6 | Highlight speaker + hard cut | QML (existe partiellement) | S |

### P1 — Le spectateur compte
| ID | Feature | Fichiers touchés | Effort |
|----|---------|------------------|--------|
| F7 | Pseudo spectateur + file oreillette nommée | bridge + QML | S |
| F8 | Toast « question lue à l'antenne » | QML | S |
| F9 | Réactions emoji (local, compteur) | bridge + QML | M |

### P1 — La preuve
| ID | Feature | Fichiers touchés | Effort |
|----|---------|------------------|--------|
| F10 | Carte source quand `evidence_used` | QML overlay | M |
| F11 | Timeline replay post-show | `runner.py` export | L |

### P2 — Le monde entre
| ID | Feature | Fichiers touchés | Effort |
|----|---------|------------------|--------|
| F12 | Sujet auto depuis tendance (optionnel) | nouveau `show/ingest.py` | L |
| F13 | Mémoire stance inter-épisodes | persistence SQLite | L |

---

## Architecture cible

```
┌──────────────┐     signaux Qt      ┌─────────────────┐
│  QML UI      │◄───────────────────│ backend_bridge  │
│  Spectateur  │                    │ ShowWorker      │
│  + Régie     │───────────────────►│ oreillette queue│
└──────────────┘   submitQuestion    └────────┬────────┘
                                            │
                                   ┌────────▼────────┐
                                   │ LangGraph show  │
                                   │ ShowState       │
                                   │ minds/tension   │
                                   └────────┬────────┘
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                           LLM          TTS (new)    export JSON
```

---

## Reclassement v4 (critère : time-to-wow)

| Rang | Option | Score |
|------|--------|-------|
| 1 | **VTV Spectateur Vivant** | 9.0 — MVP ci-dessus |
| 2 | **Le Conclave Numérique** | 8.5 — couche identité post-MVP |
| 3 | **La Régie Invisible** | 7.8 — toggle régie existe |
| 4 | **Plateau Minimaliste Cognitif** | 7.5 — coulisses = différenciation |
| 5 | **Arène Multi-LLM** | 6.8 |
| 6 | **Symposium Distribué** | 6.5 |
| 7 | **Émission 24/7** | 6.0 |
| 8 | **Studio Pédagogique** | 5.8 |
| 9 | **Pipeline Showrunner** | 5.5 |
| 10 | **Widget Embed** | 5.0 |

---

## Review itération 4

**Amélioration :** backlog actionnable, P0 clair.  
**Risque :** TTS latency peut casser l'illusion live — besoin buffer/queue audio.  
**Next :** fusionner « Conclave » + « Spectateur Vivant » en vision produit unique.
