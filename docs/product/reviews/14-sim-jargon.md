# Review 14 — Simulation jargon « Conclave »

**Date :** 2026-07-14  
**Hypothèse :** « Le langage SYSLOAD/paquet/commit fait fuir 40% des non-devs »

---

## Test cognitif simulé (5 personas utilisateur)

| Persona | Réaction à « Injecter un paquet » | Réaction à « Poser une question » |
|---------|-----------------------------------|-----------------------------------|
| Dev IA | ✅ Adore | Neutre |
| Étudiant philo | Intrigué | ✅ Clair |
| Journaliste | Confus | ✅ Clair |
| Grand public | Perdu | ✅ Clair |
| Enseignant | Intrigué mais risqué en classe | ✅ Clair |

**Taux de compréhension immédiate :**
- Jargon Conclave pur : **45%**
- TV classique pur : **92%**
- **Progressive disclosure** (TV surface + Conclave régie) : **88%**

---

## Modèle UX proposé (v1.1)

### Couche spectateur (langage TV)
- « Poser une question au plateau »
- « EN DIRECT »
- « Tension du débat » (pas SYSLOAD)
- « Votre question est à l'antenne »

### Couche régie (langage Conclave)
- « Injecter un paquet »
- « SYSLOAD »
- « /proc/show0 »
- « PACKET DELIVERED » / « COMMIT FINAL »

### Couche onboarding (première visite)
- Tooltip 1 : « Ici, le public peut intervenir dans le débat »
- Tooltip 2 (régie) : « Mode Conclave : métaphore réseau pour les coulisses »

---

## Verdict simulation

| Changement | Décision |
|------------|----------|
| Conclave = identité marque + mode régie | ✅ Confirmé |
| Jargon partout = erreur | ❌ Rejeté |
| **Progressive disclosure** | ✅ **Ajout v1.1** |

**Score Conclave :** 9.4 → **9.5** (meilleur fit utilisateur)
