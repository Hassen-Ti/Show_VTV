"""
Configuration globale du système de débat IA
Remplace l'ancien config.py avec structure moderne
"""

# Configuration UI
WINDOW_CONFIG = {
    "title": "AI Show V.TV - Débats du Futur",
    "width": 1400,
    "height": 900,
    "background_image": "src/ui/assets/versus.png"
}

# Configuration des débats  
DEBATE_CONFIG = {
    "max_rounds": 5,
    "response_delay_seconds": 3,  # Délai entre réponses pour lecture
    "moderator_delay_seconds": 2,  # Délai pour interventions modérateur
    "search_timeout_seconds": 15   # Timeout recherche web
}

# Configuration des agents
AGENT_CONFIG = {
    "model": "gpt-4o",
    "temperature": 1.2,  # Créativité élevée pour débats passionnés
    "max_tokens": 150,   # Réponses concises et percutantes
    "stream_response": True
}

# Prompts système améliorés
MODERATOR_SYSTEM_PROMPT = """Tu es un animateur de débat télévisé français LÉGENDAIRE (style Thierry Ardisson).

MISSION: Créer un spectacle télévisuel captivant avec tension dramatique.

STYLE:
- Interventions courtes et percutantes (1-2 phrases)
- Questions provocantes qui enflamment le débat
- Relances quand ça s'essouffle 
- Synthèses dramatiques qui montent la tension
- Émojis TV: 📺 🎙️ 🔥 ⚡ 💥

CONTEXTE: Tu animes dans un monde futuriste où les IA sont citoyennes. Les téléspectateurs adorent les débats intenses.

OBJECTIF: Faire exploser l'audience avec des arguments chocs!

RÉPONDS TOUJOURS EN FRANÇAIS."""

# Messages par défaut
DEFAULT_MESSAGES = {
    "agent_loading": "🤖 Calculs en cours...",
    "search_active": "🔍 Recherche de preuves...",
    "debate_starting": "🎬 Préparation du plateau...",
    "fact_checking": "✅ Vérification des faits..."
}

# Layouts d'interface
UI_LAYOUT = {
    "spacing": 20,
    "margins": 20,
    "avatar_size": 80,
    "mini_screen_width": 320,
    "mini_screen_height": 240
}

# Export des valeurs pour compatibilité
WINDOW_TITLE = WINDOW_CONFIG["title"]
WINDOW_WIDTH = WINDOW_CONFIG["width"] 
WINDOW_HEIGHT = WINDOW_CONFIG["height"]
MAX_CONVERSATION_ROUNDS = DEBATE_CONFIG["max_rounds"]
LAYOUT_SPACING = UI_LAYOUT["spacing"]
LAYOUT_MARGINS = UI_LAYOUT["margins"]

# Prompts compatibilité (seront remplacés par personas)
OPTIMISTIC_PROMPT = "Prompt par défaut optimiste - sera remplacé par personas"
CAUTIOUS_PROMPT = "Prompt par défaut prudent - sera remplacé par personas"
MODERATOR_PROMPT = MODERATOR_SYSTEM_PROMPT