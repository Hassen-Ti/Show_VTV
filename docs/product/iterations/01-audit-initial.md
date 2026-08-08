# Itération 1 — Audit produit initial

**Date :** 2026-07-14  
**Rôle :** Product AI Owner  
**Méthode :** lecture codebase + screenshots + benchmark web

---

## Ce que Show V.TV est aujourd'hui

Un **simulateur de plateau TV** local (PyQt6 + QML) branché sur un moteur LangGraph (`src/show/`) :

| Couche | État | Force | Lacune |
|--------|------|-------|--------|
| Cognition | Mature | Personas vectorisées, topologies cognitives, `stance_history`, tension | Pas de mémoire inter-épisodes |
| Modération | Fonctionnel | Mr Bullshit, interjections, oreillette spectateur | Pas de scoring, pas de fact-check visible |
| UI | Soignée | Mode spectateur, régie masquée, design tokens studio | Texte seul, pas de voix ni avatar animé |
| Distribution | Absente | CLI headless + export JSON | Pas de stream, pas de clips, pas de web |
| Monde | Implicite | Sujets IA & société | Pas de métaphore « monde dans l'ordi » |

**Verdict itération 1 :** excellent *moteur de pensée conflictuelle*, faible *expérience médiatique vivante*.

---

## Question centrale

> Si le monde vivait dans un ordinateur et sur internet, que serait un plateau TV virtuel ? Que seraient ces agents ?

**Réponse v0 (brute) :**  
Un plateau TV virtuel serait une **salle de protocole** — un endroit où des entités logicielles (APIs, modèles, communautés, flux de données) se rencontrent pour négocier le sens du monde en temps réel. Les agents ne seraient pas des « personnes » mais des **ambassadeurs de sous-mondes numériques** : le provocateur = le feed Twitter, le diplomate = la modération Wikipédia, le modérateur = le protocole HTTP qui impose tour de parole.

---

## 10 options produit (v1 — classement provisoire)

| # | Option | Pitch | Score /10 |
|---|--------|-------|-----------|
| 1 | **Le Conclave Numérique** | Débat live où chaque invité incarne une *fonction internet* (algo, communauté, protocole) ; le public via oreillette = paquets réseau injectés dans le flux | 8.2 |
| 2 | **VTV Spectateur Vivant** | Polish du produit actuel + voix TTS + jauges tension + replays | 7.8 |
| 3 | **Symposium Distribué** | Agents sur machines séparées, amphithéâtre web (cf. imagineering-cc/symposium) | 7.5 |
| 4 | **La Régie Invisible** | UX régie/producer-first : contrôle plateau IA pour créateurs | 7.0 |
| 5 | **Émission Autonome 24/7** | Twitch bot débats tendances Reddit (cf. A Bot's Take) | 6.8 |
| 6 | **Arène Multi-LLM** | Un modèle par persona, transparence coût (cf. VoxArena) | 6.5 |
| 7 | **Studio Pédagogique** | Débats formatés pour salles de classe | 6.2 |
| 8 | **Pipeline Showrunner** | Sortie vidéo cinématique 6 scènes (cf. Showrunner) | 6.0 |
| 9 | **Plateau Minimaliste Cognitif** | UX centrée coulisses / monologue intérieur | 5.5 |
| 10 | **Widget Débat Embed** | iframe débat pour médias | 5.0 |

---

## Ce qui manque (gap analysis)

1. **Voix** — le plateau est muet ; la TV est audio-first
2. **Corps** — pas d'embodiment ; les agents sont des flux texte
3. **Temporalité broadcast** — pas de direct, pas de replay, pas d'EPG
4. **Boucle internet** — recherche web existe mais pas d'ingestion flux live (trends, news)
5. **Économie du spectacle** — pas de récompense spectateur, pas de clips viraux
6. **Identité des agents** — personas génériques, pas d'ancrage « natif réseau »
7. **Narration longue** — un débat = une session ; pas de saison, pas d'arc
8. **Preuve** — pas de cartes d'argument, pas de sources citées à l'écran
9. **Social** — oreillette = début ; pas de vote, réaction, partage
10. **Manifeste** — le *pourquoi* philosophique n'est pas dans le produit

---

## Benchmark web (itération 1)

| Projet | Insight pour VTV |
|--------|------------------|
| [JedAI Council](https://jedaicouncil.com/) | Chambre 3D + cast divers + production auto |
| [VoxArena](https://voxarena.ai/how-it-works) | Pipeline 7 étapes, TTS prosodie, novelty gate |
| [Symposium](https://github.com/imagineering-cc/symposium) | DNA markdown par figure, LiveKit distribué |
| [Showrunner](https://github.com/divi-vijayakumar/Showrunner/) | Continuité cast/set/scène comme code |
| [AITV.GG](https://aitv.gg/) | Spectateur co-créateur + tokens |
| [AI Podcast Studio](https://github.com/mohamdImran/ai-podcast-studio) | Q&A live injectée dans flux audio |

---

## Review itération 1

**Forces :** bon diagnostic technique, métaphore « protocole » prometteuse.  
**Faiblesses :** classement encore générique ; pas assez ancré dans les assets existants (oreillette, coulisses, mind state).  
**Prochaine itération :** resserrer sur la métaphore « monde dans l'ordi » et scorer chaque option vs effort/ROI.
