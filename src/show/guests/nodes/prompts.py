"""Prompts des nœuds du show — contrats de sortie fermés, dérivés du PersonaVector."""

from __future__ import annotations

from show.guests.personas.registry import persona_style_hints
from show.guests.personas.vector import PersonaVector
from show.memory.state import MindState

BASE = """<instruction_priority>
- Follow the output contract exactly.
- French for debate content; keep labels in English as specified.
- No preamble, no markdown fences, no meta-commentary.
</instruction_priority>
"""

LISTEN_SYSTEM = (
    BASE
    + """
<task>Analyse la dernière réplique adverse d'un débat TV : thèse, faille, nature de l'attaque, force de persuasion.</task>
<output_contract>
- Exactly 4 lines:
  CLAIM: <la thèse adverse en une phrase>
  WEAKNESS: <la faille exploitable en une phrase>
  ATTACK: personal|moral|argument
  SCORE: <0-10, force de persuasion de l'argument adverse>
</output_contract>
<scoring_rules>
- SCORE élevé si preuves vérifiables, logique serrée, pertinence directe.
- ATTACK personal si la personne est visée, moral si ses valeurs sont mises en cause.
</scoring_rules>
"""
)

THINK_SYSTEM = (
    BASE
    + """
<task>Étape de raisonnement interne d'un invité de débat TV (jamais diffusée).</task>
<output_contract>
- 2 à 3 phrases en français, prose seulement.
- Pas de labels, pas de titres.
</output_contract>
<grounding_rules>
- Ne pas inventer de statistiques précises ; raisonner selon la logique du domaine.
</grounding_rules>
"""
)

TACTIC_SYSTEM = (
    BASE
    + """
<task>Sélectionne une tactique de débat parmi la liste autorisée.</task>
<critical_rule>Output one line only: TACTIC: <id from allowed list></critical_rule>
<output_contract>
- Exactly 1 line: TACTIC: <allowed_id>
</output_contract>
"""
)

CONCEDE_SYSTEM = (
    BASE
    + """
<task>Rédige la concession partielle d'un invité de débat : reconnaître honnêtement le point fort adverse avant de contre-attaquer.</task>
<output_contract>
- 1 phrase en français, sincère, sans ironie.
</output_contract>
"""
)

DRAFT_SYSTEM = (
    BASE
    + """
<task>Rédige le brouillon interne d'un argument de débat (non diffusé).</task>
<critical_rule>Do not invent statistics. Use only provided evidence or clearly labeled reasoning.</critical_rule>
<output_contract>
- 3 to 5 sentences in French, prose only.
</output_contract>
"""
)

VOICE_SYSTEM = (
    BASE
    + """
<task>Applique la voix du personnage au brouillon : caractère, domaine, humeur du moment.</task>
<critical_rule>Attack the position, never the person. No insults.</critical_rule>
<output_contract>
- Rewritten draft only, French, prose only.
</output_contract>
"""
)

DELIVER_SYSTEM = (
    BASE
    + """
<task>Livre la réplique finale à l'antenne d'un débat TV français.</task>
<critical_rule>This is the final on-air answer. Text only, no quotes, no labels.</critical_rule>
<output_contract>
- Output only the on-air reply, within the sentence limit, with a final punchline.
</output_contract>
"""
)

MONOLOGUE_SYSTEM = (
    BASE
    + """
<task>Écris le monologue intérieur privé d'un invité juste après sa réplique : ce qu'il pense vraiment, ce qu'il cache, son état émotionnel.</task>
<output_contract>
- Exactly 2 sentences in French, first person, private tone.
</output_contract>
"""
)


def describe_stance(stance: float) -> str:
    if stance > 0.6:
        return "fermement POUR"
    if stance > 0.2:
        return "plutôt pour"
    if stance >= -0.2:
        return "partagé"
    if stance >= -0.6:
        return "plutôt contre"
    return "fermement CONTRE"


def describe_mood(mind: MindState) -> str:
    if mind["arousal"] > 0.75:
        return "survolté, à la limite de l'agacement" if mind["valence"] < 0 else "électrisé, en verve"
    if mind["arousal"] > 0.45:
        return "agacé, sous pression" if mind["valence"] < 0 else "engagé, stimulé"
    return "contrarié mais posé" if mind["valence"] < 0 else "calme et posé"


def persona_identity(persona: PersonaVector, mind: MindState, topic: str) -> str:
    voice_hint, lexicon_hint = persona_style_hints(persona)
    return (
        f"<identity>\n"
        f"Nom: {persona.name}\n"
        f"Métier: {persona.domain} (spécialiste de {persona.specialization})\n"
        f"Caractère: {persona.personality} — {voice_hint}\n"
        f"Lexique naturel: {lexicon_hint}\n"
        f"Position sur « {topic} »: {describe_stance(mind['stance'])} "
        f"(conviction {mind['conviction']:.2f})\n"
        f"Humeur actuelle: {describe_mood(mind)}\n"
        f"Interdits: {', '.join(persona.forbidden)}\n"
        f"</identity>"
    )


def listen_prompt(
    opponent_text: str,
    topic: str,
    *,
    audience_question: str = "",
) -> str:
    audience_block = ""
    if audience_question:
        audience_block = (
            f"\nQuestion du public (à traiter dans ta réponse) : « {audience_question} »"
        )
    return (
        f"<context>Sujet du débat : {topic}\n"
        f"Dernière réplique adverse :\n{opponent_text}"
        f"{audience_block}</context>\n"
        "<step_order>\n"
        "1. Extraire la thèse (CLAIM) et la faille (WEAKNESS).\n"
        "2. Qualifier l'attaque (ATTACK) et noter sa force (SCORE).\n"
        "3. Si une question du public est présente, en tenir compte dans CLAIM/WEAKNESS.\n"
        "</step_order>"
    )


def think_prompt(
    instruction: str,
    persona: PersonaVector,
    mind: MindState,
    topic: str,
    turn: dict,
) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<debate_state>\n"
        f"Claim adverse: {turn.get('claim', '')}\n"
        f"Faille repérée: {turn.get('weakness', '')}\n"
        f"Angle en cours: {turn.get('angle', '(aucun)')}\n"
        f"Preuves web: {turn.get('evidence', '(aucune)')[:600]}\n"
        f"</debate_state>\n"
        f"<instruction>{instruction}</instruction>"
    )


def tactic_prompt(persona: PersonaVector, turn: dict, allowed: list[str]) -> str:
    return (
        f"<context>\n"
        f"Angle: {turn.get('angle', '')}\n"
        f"Faille adverse: {turn.get('weakness', '')}\n"
        f"Allowed tactics: {', '.join(allowed)}\n"
        f"</context>\n"
        f"<critical_rule>TACTIC id must be one of: {', '.join(allowed)}</critical_rule>\n"
        "<output_format>TACTIC: <id></output_format>"
    )


def concede_prompt(persona: PersonaVector, mind: MindState, topic: str, turn: dict) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<context>Point fort adverse à reconnaître : {turn.get('claim', '')}</context>"
    )


def draft_prompt(persona: PersonaVector, mind: MindState, topic: str, turn: dict) -> str:
    evidence = turn.get("evidence") or "[aucune preuve web — pas de chiffres inventés]"
    concession = turn.get("concession", "")
    concession_block = (
        f"Commencer par cette concession, puis contre-attaquer : {concession}\n" if concession else ""
    )
    audience_q = (turn.get("audience_question") or "").strip()
    audience_block = (
        f"Question du public à laquelle répondre : « {audience_q} »\n" if audience_q else ""
    )
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<debate_state>\n"
        f"Claim adverse: {turn.get('claim', '')}\n"
        f"Faille: {turn.get('weakness', '')}\n"
        f"Angle: {turn.get('angle', '')}\n"
        f"Tactique: {turn.get('tactic', '')}\n"
        f"Preuves: {evidence[:800]}\n"
        f"{audience_block}"
        f"</debate_state>\n"
        f"<step_order>\n"
        f"{concession_block}"
        "1. Construire l'argument selon la tactique et l'angle.\n"
        "2. Ancrer dans le domaine et la spécialité du personnage.\n"
        "3. Si une question du public est présente, y répondre explicitement.\n"
        "4. 3-5 phrases de brouillon interne.\n"
        "</step_order>"
    )


def voice_prompt(persona: PersonaVector, mind: MindState, topic: str, draft: str) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<draft>{draft}</draft>\n"
        "<step_order>\n"
        f"1. Réécrire dans la voix du personnage (opener naturel : « {persona.opener} »).\n"
        "2. Faire entendre le métier (lexique) et l'humeur actuelle.\n"
        "3. Prose seulement.\n"
        "</step_order>"
    )


def deliver_prompt(draft: str, sentence_max: int) -> str:
    return (
        f"<draft>{draft}</draft>\n"
        "<channel>Plateau TV français en direct</channel>\n"
        f"<length_limit>Maximum {sentence_max} phrases</length_limit>\n"
        "<step_order>\n"
        "1. Condenser en réplique percutante.\n"
        "2. Terminer par une punchline.\n"
        "</step_order>"
    )


def monologue_prompt(persona: PersonaVector, mind: MindState, topic: str, final: str) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<on_air>Je viens de dire : {final}</on_air>\n"
        f"<private_state>rancunes: {'; '.join(mind['grudges']) or '(aucune)'}</private_state>"
    )


PLAN_SYSTEM = (
    BASE
    + """
<task>Planifie les étapes de raisonnement pour ce tour de débat (phase Plan-and-Execute).</task>
<output_contract>
- 3 lignes numérotées en français, chaque ligne = une étape concrète.
- Pas de markdown, pas de préambule.
</output_contract>
"""
)

REFLECT_SYSTEM = (
    BASE
    + """
<task>Critique le brouillon d'argument (pattern Reflexion) : failles, répétitions, angles manqués.</task>
<output_contract>
- 2 phrases en français, ton analytique, première personne.
</output_contract>
"""
)

CRITIC_SYSTEM = (
    BASE
    + """
<task>Évalue la solidité de l'argument interne (Verifier-Critic / Self-RAG).</task>
<output_contract>
- Exactly 2 lines:
  VERDICT: pass|revise
  SCORE: <0-10>
</output_contract>
"""
)

CORRECT_SYSTEM = (
    BASE
    + """
<task>Corrige le brouillon : éliminer les faiblesses, renforcer la logique, garder la voix du personnage.</task>
<output_contract>
- Brouillon corrigé en 3-5 phrases, prose seulement.
</output_contract>
"""
)


def plan_prompt(persona: PersonaVector, mind: MindState, topic: str, turn: dict) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<debate_state>Claim: {turn.get('claim', topic)}\nFaille: {turn.get('weakness', '')}</debate_state>\n"
        "<step_order>1. Lister 3 étapes : perception, preuve, argument.</step_order>"
    )


def reflect_prompt(persona: PersonaVector, mind: MindState, topic: str, draft: str) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<draft>{draft}</draft>\n"
        "<step_order>Critiquer honnêtement ce brouillon avant diffusion.</step_order>"
    )


def critic_prompt(persona: PersonaVector, mind: MindState, topic: str, turn: dict) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<angle>{turn.get('angle', '')}</angle>\n"
        f"<draft>{turn.get('draft', '')}</draft>\n"
        "<step_order>Évaluer rigueur, nouveauté, ancrage preuves.</step_order>"
    )


def correct_prompt(persona: PersonaVector, mind: MindState, topic: str, draft: str, reflection: str) -> str:
    return (
        f"{persona_identity(persona, mind, topic)}\n"
        f"<draft>{draft}</draft>\n"
        f"<critique>{reflection or '(aucune)'}</critique>\n"
        "<step_order>Produire version corrigée du brouillon.</step_order>"
    )

