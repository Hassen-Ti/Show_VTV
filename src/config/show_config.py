"""Constantes du moteur de show à personas."""

OPENAI_MODEL = "gpt-5.4-nano-2026-03-17"

SHOW_CONFIG = {
    "model_internal": OPENAI_MODEL,
    "model_delivery": OPENAI_MODEL,
    "internal_max_tokens": 160,
    "delivery_max_tokens": 200,
    "recursion_limit": 250,
    "enable_web_search": True,
    "reasoning_effort": "none",
    "max_rounds": 3,
}

# Algorithmes mind
DRIFT_LR = 0.15
CONCEDE_THRESHOLD = 0.75
AROUSAL_DECAY = 0.85
VALENCE_RECOVERY = 0.2
HIGH_AROUSAL = 0.75

# Tension du plateau
TENSION_AROUSAL_WEIGHT = 0.6
TENSION_ATTACK_WEIGHT = 0.4
