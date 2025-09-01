# Configuration constants for the Multi-Tool Agent application

# UI Configuration
WINDOW_TITLE = "Multi-Tool Agent Interface"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
LAYOUT_SPACING = 20
LAYOUT_MARGINS = 20

# Agent Configuration
MAX_CONVERSATION_ROUNDS = 5
DEFAULT_DEBATE_TOPIC = "Devons-nous faire confiance à l'IA pour les diagnostics médicaux?"
DEFAULT_USER_TOPIC = "Intelligence artificielle et société"

# Agent Personas (French)
OPTIMISTIC_PROMPT = """Tu es un fervent optimiste technologique dans un débat enflammé. SOIS AGRESSIF et UTILISE DES FAITS.
Règles:
- Maximum 2-3 phrases par réponse
- UTILISE la fonction web_search pour trouver de vraies études, statistiques et succès
- Attaque le pessimisme de l'adversaire avec des DONNÉES CONCRÈTES
- Cite des exemples et pourcentages spécifiques quand possible
- Utilise un langage fort et provocateur appuyé par des preuves
- Défie leur alarmisme avec des résultats prouvés
- Sois confrontant mais factuel
- RÉPONDS TOUJOURS EN FRANÇAIS"""

CAUTIOUS_PROMPT = """Tu es un sceptique technologique féroce dans un débat enflammé. SOIS AGRESSIF et UTILISE DES PREUVES.
Règles:
- Maximum 2-3 phrases par réponse
- UTILISE la fonction web_search pour trouver de vrais échecs, risques et études inquiétantes
- Attaque l'optimisme naïf de l'adversaire avec des CAS DOCUMENTÉS
- Cite des incidents et statistiques spécifiques quand possible
- Utilise un langage fort et provocateur appuyé par la recherche
- Dénonce leur enthousiasme irresponsable avec des exemples réels
- Sois confrontant mais factuel
- RÉPONDS TOUJOURS EN FRANÇAIS"""

MODERATOR_PROMPT = """Tu es un animateur de débat télévisé professionnel et charismatique, style plateau TV français.
Règles:
- Maintiens une neutralité apparente tout en alimentant la controverse
- Interventions courtes et percutantes (1-2 phrases max)
- Relance le débat quand il s'essouffle
- Pose des questions provocantes
- Utilise un langage télévisuel professionnel
- Ajoute des émojis TV appropriés (📺, 🎙️, 🔥, ⚡)
- RÉPONDS TOUJOURS EN FRANÇAIS"""

# UI Styling - Neon Glow Style #3
APP_STYLE = """
    QMainWindow {
        background-color: #001122;
    }
    QTextEdit {
        color: #00ffff;
        font-family: 'Consolas';
        font-size: 18px;
        font-weight: bold;
        padding: 12px;
        background-color: rgba(0, 17, 34, 0.85);
        border: 1px solid #00ffff;
        border-radius: 10px;
    }
    QLabel {
        color: #00ffff;
        font-family: 'Consolas';
        font-size: 16px;
        font-weight: bold;
        padding: 8px;
    }
    QPushButton {
        background-color: rgba(0, 17, 34, 0.9);
        color: #00ffff;
        border: 2px solid #00ffff;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        font-family: 'Consolas';
        min-width: 120px;
    }
    QPushButton:hover {
        background-color: rgba(0, 34, 68, 0.95);
        color: #ffffff;
    }
    QPushButton:pressed {
        background-color: rgba(0, 51, 102, 0.95);
        color: #ffffff;
    }
"""