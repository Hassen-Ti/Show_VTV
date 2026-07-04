"""Constantes du moteur de show à personas (voir docs/superpowers/specs/2026-07-02)."""

from config.settings import OPENAI_MODEL

SHOW_CONFIG = {
    "model_internal": OPENAI_MODEL,
    "model_delivery": OPENAI_MODEL,
    "internal_max_tokens": 160,
    "delivery_max_tokens": 200,
    "recursion_limit": 250,
    "enable_web_search": True,
}

# Algorithmes mind
DRIFT_LR = 0.15               # vitesse de dérive d'opinion
CONCEDE_THRESHOLD = 0.75      # persuasion au-delà de laquelle on concède
AROUSAL_DECAY = 0.85          # décroissance émotionnelle par round
VALENCE_RECOVERY = 0.2        # retour de la valence vers la baseline par round
HIGH_AROUSAL = 0.75           # seuil "à chaud" : répliques sèches, tactiques agressives

# Tension du plateau
TENSION_AROUSAL_WEIGHT = 0.6
TENSION_ATTACK_WEIGHT = 0.4
