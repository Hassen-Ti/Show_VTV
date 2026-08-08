# Itération 5 — Fusion produit : « V.TV Le Conclave »

**Date :** 2026-07-14  
**Input :** itérations 1–4 + benchmark VoxArena, JedAI Council

---

## Insight de fusion

**VTV Spectateur Vivant** (exécution) + **Le Conclave Numérique** (âme) = un seul produit :

> **V.TV — Le Conclave**  
> *Plateau de débat où les processus du monde numérique s'affrontent en direct, sous les yeux du public connecté.*

Les invités actuels (provocateur, diplomate, cérébral) deviennent des **archétypes d'entités réseau** :

| Persona actuelle | Identité Conclave | Voix TTS | Couleur |
|------------------|-------------------|----------|---------|
| `provocateur` | **Le Flux** — viralité, hot takes, vitesse | Rapide, énergique | coral |
| `diplomate` | **Le Protocole** — consensus, modération, RFC | Posée, chaleureuse | blue |
| `cerebral` | **L'Archive** — profondeur, sources, long terme | Lente, grave | gold |
| Mr Bullshit | **Le Scheduler** — alloue la parole, garde le temps | Neutre, autoritaire | blanc |

Chaque débat = un **syscall public** : le sujet est une décision que le monde numérique doit trancher.

---

## Mécaniques signature

### 1. Oreillette = Injection de paquet
- Le spectateur n'envoie pas une « question » — il **injecte un paquet** dans le bus
- UI : champ renommé « **Injecter dans le flux** »
- File = buffer réseau (max 3 ✅ déjà implémenté)
- Quand lu : animation « PACKET DELIVERED » cyan

### 2. Tension = Charge système
- Jauge existante (`tension` dans `ShowState`) rebaptisée **SYSLOAD**
- Seuils : &lt;0.3 stable, 0.3–0.7 élevée, &gt;0.7 → `moderator_interject` = **kernel panic évitée**

### 3. Coulisses = `/proc/show`
- Mode régie révèle les mind states = **process introspection**
- `stance_history` = log de commits sur la position

### 4. Stance drift = mise à jour live
- Quand un invité concède → animation « PATCH APPLIED »
- Déjà dans le moteur (`mind.py`) — juste à surfacer

---

## Ce que la concurrence fait mieux (à voler)

| Concurrent | Feature | Adaptation VTV |
|------------|---------|----------------|
| VoxArena | Novelty gate (anti-répétition) | Cosine similarity sur 3 derniers tours |
| VoxArena | TTS prosodie par persona | Mapper `arousal_gain` → vitesse TTS |
| JedAI Council | Chambre 3D | Phase 3 — pas MVP |
| Symposium | DNA markdown par figure | `PersonaVector` = déjà le DNA |
| AI Podcast Studio | Q&A injectée audio | Oreillette → TTS réponse mid-show |
| debate-agents | Cartes d'argument | UI cards pour chaque tour |

---

## Classement v5 — produit fusionné en tête

| Rang | Option | Statut |
|------|--------|--------|
| **1** | **V.TV Le Conclave** (fusion) | ★ RECOMMANDÉ |
| 2 | VTV Spectateur Vivant (seul) | absorbé dans #1 |
| 3 | Plateau Minimaliste Cognitif | feature « /proc » |
| 4 | La Régie Invisible | mode régie du Conclave |
| 5–10 | (inchangé, dépriorisé) | extensions futures |

---

## Review itération 5

**Amélioration :** vision produit unique, ancrée dans le code existant.  
**Manque :** réponse philosophique finale structurée, spec design complète.  
**Next :** rédiger la réponse manifeste + wireframes textuels détaillés.
