"""
Topics de débat IA réalistes - Contexte 2025
5 sujets d'actualité pour débats télévisés
"""

TOPICS = {
    "remplacement_emplois": {
        "title": "IA et Emplois: Révolution ou Désastre Social?",
        "question": "Faut-il accélérer l'automatisation par IA malgré les suppressions d'emplois massives?",
        "context": "2025: ChatGPT, Claude, Copilot remplacent déjà des milliers d'emplois. 40% des tâches automatisables d'ici 2030.",
        "stakes": "Productivité économique vs. Chômage de masse et inégalités sociales"
    },
    
    "education_ia": {
        "title": "IA à l'École: Assistant ou Remplaçant?", 
        "question": "L'IA doit-elle remplacer les professeurs dans l'enseignement personnalisé?",
        "context": "2025: ChatGPT utilisé par 89% des étudiants. IA tutorat 24h/24 plus efficace que cours traditionnels.",
        "stakes": "Éducation optimisée vs. Perte du lien humain et créativité"
    },
    
    "sante_diagnostic": {
        "title": "IA Médicale: Révolution ou Risque?",
        "question": "Les diagnostics médicaux doivent-ils être confiés prioritairement à l'IA plutôt qu'aux médecins?", 
        "context": "2025: IA détecte cancers avec 95% précision vs 87% radiologues. Google DeepMind, GPT-4V analysent déjà des millions d'images.",
        "stakes": "Précision diagnostique vs. Responsabilité médicale humaine"
    },
    
    "surveillance_ia": {
        "title": "Surveillance IA: Sécurité ou Dictature?",
        "question": "Faut-il autoriser la surveillance généralisée par IA pour prévenir crimes et terrorisme?",
        "context": "2025: Reconnaissance faciale IA, analyse comportementale temps réel. Chine surveille 1.4 milliard de citoyens par IA.",
        "stakes": "Sécurité publique maximale vs. Vie privée et libertés individuelles"
    },
    
    "creation_ia": {
        "title": "Art par IA: Créativité ou Contrefaçon?",
        "question": "L'art généré par IA (Midjourney, DALL-E) doit-il avoir les mêmes droits que l'art humain?",
        "context": "2025: IA génère films, musiques, romans. 60% du contenu web créé par IA d'ici 2026.",
        "stakes": "Démocratisation créative vs. Dévalorisation travail artistique humain"
    }
}

# Topics par domaine de persona
DOMAIN_TOPICS = {
    "economie_emplois": "remplacement_emplois",
    "education_ia": "education_ia", 
    "sante_diagnostic": "sante_diagnostic",
    "surveillance_securite": "surveillance_ia",
    "art_creation": "creation_ia"
}

def get_topic(topic_id):
    """Récupère un topic complet"""
    return TOPICS.get(topic_id, None)

def get_topic_for_domain(domain):
    """Récupère le topic associé à un domaine de persona"""
    topic_id = DOMAIN_TOPICS.get(domain)
    return get_topic(topic_id) if topic_id else None

def get_all_topics():
    """Liste tous les topics disponibles"""
    return TOPICS

def format_topic_for_debate(topic_id):
    """Formate un topic pour le débat"""
    topic = get_topic(topic_id)
    if topic:
        return f"""🎬 SUJET DU DÉBAT 🎬

{topic['title']}

QUESTION: {topic['question']}

CONTEXTE: {topic['context']}

ENJEUX: {topic['stakes']}

Que le meilleur argument gagne! 🔥⚡"""
    return None