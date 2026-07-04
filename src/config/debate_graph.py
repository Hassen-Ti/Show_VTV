"""Configuration du graphe débatteur ONPC (nodes, personas, tactiques)."""

from config.settings import OPENAI_MODEL

DEBATE_GRAPH_CONFIG = {
    "model_internal": OPENAI_MODEL,
    "model_delivery": OPENAI_MODEL,
    "reasoning_effort": "none",
    "recursion_limit": 12,
    "enable_step_callbacks": True,
    "skip_search_round_1": False,
    "internal_max_tokens": 120,
    "delivery_max_tokens": 200,
}

TACTICS = frozenset(
    {
        "clash",
        "contradiction",
        "pivot",
        "pivot_future",
        "moral_attack",
        "expose_hypocrisy",
        "dismiss_fear",
    }
)

STEP_LABELS = {
    "parse_opponent": "🎯 Analyse de l'adversaire…",
    "choose_frame": "🎬 Choix de l'angle d'attaque…",
    "search_web": "🔍 Recherche d'un fait choc…",
    "select_tactic": "⚔️ Préparation de la riposte…",
    "draft_argument": "✍️ Construction de l'argument…",
    "apply_character": "🎭 Mise en voix…",
    "polish_onpc": "📺 Finalisation plateau…",
}

PERSONA_OPTIMISTE = {
    "name": "Optimiste ONPC",
    "cognitive": "accelerating",
    "affective": "triumphant",
    "rhetoric": "journalist",
    "tactics": ["clash", "pivot_future", "dismiss_fear"],
    "concession_rate": 0.1,
    "sentence_max": 2,
    "opener": "Soyons sérieux :",
    "temperature_facts": 0.4,
    "temperature_voice": 1.3,
    "forbidden": ["insulte", "injure", "attaque personnelle"],
}

PERSONA_SCEPTIQUE = {
    "name": "Sceptique ONPC",
    "cognitive": "pragmatic",
    "affective": "indignant",
    "rhetoric": "journalist",
    "tactics": ["contradiction", "moral_attack", "expose_hypocrisy"],
    "concession_rate": 0.0,
    "sentence_max": 2,
    "opener": "Mais attendez —",
    "temperature_facts": 0.3,
    "temperature_voice": 1.2,
    "forbidden": ["insulte", "injure", "attaque personnelle"],
}

PERSONA_VECTOR_KEYS = frozenset(
    {
        "name",
        "cognitive",
        "affective",
        "rhetoric",
        "tactics",
        "concession_rate",
        "sentence_max",
        "opener",
        "temperature_facts",
        "temperature_voice",
        "forbidden",
    }
)


def get_persona_vector(side: str) -> dict:
    if side == "sceptique":
        return dict(PERSONA_SCEPTIQUE)
    return dict(PERSONA_OPTIMISTE)


def validate_persona_vector(vector: dict) -> list[str]:
    errors: list[str] = []
    missing = PERSONA_VECTOR_KEYS - set(vector.keys())
    if missing:
        errors.append(f"clés manquantes: {sorted(missing)}")
    for tactic in vector.get("tactics", []):
        if tactic not in TACTICS:
            errors.append(f"tactique inconnue: {tactic}")
    return errors
