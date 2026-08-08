# Itération 9 — Roadmap & spec technique audio

**Date :** 2026-07-14

---

## Roadmap 3 phases

### Phase 1 — Allumer (MVP, 4–6 sem)
**Objectif :** le plateau passe de texte à *expérience broadcast*.

- [ ] `show/tts.py` — wrapper OpenAI TTS / ElevenLabs
- [ ] Queue audio dans `ShowWorker` (éviter overlap speakers)
- [ ] Binding SYSLOAD → jauge QML
- [ ] Silhouettes pulse (RMS)
- [ ] Sons studio (room tone, stings)
- [ ] Renaming UX : « Injecter un paquet », rôles Conclave
- [ ] Overlay PACKET DELIVERED / PATCH APPLIED

**Critère succès :** un non-dev dit « ça ressemble à une émission » en 30s.

### Phase 2 — Approfondir (8–12 sem)
**Objectif :** le Conclave devient un produit complet.

- [ ] Cartes d'argument + sources (`evidence_used`)
- [ ] Novelty gate anti-répétition
- [ ] Timeline replay post-show
- [ ] Persistance `stance_history` inter-syscalls
- [ ] Ingestion sujet tendance (optionnel)
- [ ] Export clip « best moment »
- [ ] Multi-LLM par persona (badge régie)

**Critère succès :** session de 30 min engageante sans fatigue.

### Phase 3 — Diffuser (16+ sem)
**Objectif :** le monde peut regarder.

- [ ] Viewer web (WebSocket + transcript live)
- [ ] Stream Twitch/YouTube (OBS bridge)
- [ ] Peer authentication + paquets nommés
- [ ] Chambre 3D légère (Three.js)
- [ ] API embed widget presse
- [ ] Kernel (saisons de syscalls)

---

## Spec technique TTS

```python
# show/tts.py (proposition)
@dataclass
class VoiceProfile:
    speaker_id: str
    voice: str           # "alloy", "nova", etc.
    rate: float          # 0.8–1.2, lié à arousal_gain
    pitch: float         # optionnel

def synthesize(text: str, profile: VoiceProfile) -> bytes:
    """Retourne MP3/WAV."""

def prosody_from_persona(persona: PersonaVector) -> VoiceProfile:
    rate = 1.0 + (persona.arousal_gain - 0.5) * 0.3
    ...
```

### Pipeline audio dans ShowWorker

```
messageStream (char) ──► buffer texte
messageComplete ──► synthesize() ──► audio queue ──► play()
                                      │
                                      └──► signal rmsLevel(speaker, float)
```

**Latence cible :** &lt;2s entre fin texte et début audio (pré-fetch pendant stream chars).

### Mapping persona → voix Conclave

| Rôle | Voice | Rate |
|------|-------|------|
| Le Flux (provocateur) | nova | 1.15 |
| Le Protocole (diplomate) | alloy | 0.95 |
| L'Archive (cérébral) | onyx | 0.85 |
| Le Scheduler (mod) | echo | 1.0 |

---

## Risques & mitigations

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Latence TTS | Casse l'illusion | Queue + pré-fetch ; afficher « buffering » discret |
| Coût API | $ par show | Mode mock TTS local (pyttsx3) pour dev |
| PyQt6 seulement | Pas de web | Phase 3 : bridge WebSocket |
| Répétition LLM | Ennui | Novelty gate phase 2 |

---

## Review itération 9

**Amélioration :** roadmap chiffrée, spec TTS concrète.  
**Next :** document final consolidé.
