"""Micro-prompts utilisateur des nœuds — optimisés GPT-5.4 nano (sorties fermées)."""

from __future__ import annotations


def parse_prompt(opponent_last: str, is_round_one: bool) -> str:
    if is_round_one:
        return (
            "<task_update>Premier tour : pas de réplique adverse encore.</task_update>\n"
            f"<context>Sujet du débat : {opponent_last}</context>\n"
            "<step_order>\n"
            "1. Déduire la thèse implicite de la position adverse sur ce sujet.\n"
            "2. Identifier la faille exploitable en clash TV.\n"
            "3. Émettre exactement 2 lignes labelisées.\n"
            "</step_order>\n"
            "<example>\n"
            "CLAIM: L'IA détruit massivement l'emploi sans recours.\n"
            "WEAKNESS: Aucune stat récente ne soutient une destruction nette.\n"
            "</example>"
        )
    return (
        f"<context>Dernière réplique adverse :\n{opponent_last}</context>\n"
        "<step_order>\n"
        "1. Extraire la thèse principale (CLAIM).\n"
        "2. Trouver la faille logique, factuelle ou rhétorique (WEAKNESS).\n"
        "3. Émettre exactement 2 lignes labelisées.\n"
        "</step_order>\n"
        "<edge_cases>\n"
        "- Si la réplique est vague : WEAKNESS = manque de preuves ou contradiction interne.\n"
        "- Si plusieurs thèses : retenir la plus attaquable.\n"
        "</edge_cases>"
    )


def frame_prompt(
    parsed_claim: str,
    weakness: str,
    topic: str,
    rhetoric: str,
) -> str:
    return (
        f"<context>\n"
        f"Topic: {topic}\n"
        f"Claim: {parsed_claim}\n"
        f"Weakness: {weakness}\n"
        f"Rhetoric: {rhetoric}\n"
        "</context>\n"
        "<step_order>\n"
        "1. Choisir un angle d'attaque ONPC en une phrase (FRAME).\n"
        "2. Décider si une preuve web est nécessaire (NEEDS_EVIDENCE: oui|non).\n"
        "3. Si oui, formuler une requête web courte (EVIDENCE_QUERY).\n"
        "</step_order>\n"
        "<example>\n"
        "FRAME: Retourner l'angoisse contre les données réelles du marché.\n"
        "NEEDS_EVIDENCE: oui\n"
        "EVIDENCE_QUERY: créations emploi IA France 2025\n"
        "</example>"
    )


def tactic_prompt(
    frame: str,
    allowed_tactics: list[str],
    affective: str,
    is_round_one: bool,
) -> str:
    tactics = ", ".join(allowed_tactics)
    round_hint = (
        "Premier tour : choisir pivot ou clash sur le cadrage du sujet."
        if is_round_one
        else "Réplique directe à l'adversaire."
    )
    return (
        f"<context>\n"
        f"Frame: {frame}\n"
        f"Allowed tactics: {tactics}\n"
        f"Tone: {affective}\n"
        f"Round: {round_hint}\n"
        "</context>\n"
        f"<critical_rule>TACTIC id must be one of: {tactics}</critical_rule>\n"
        "<output_format>TACTIC: <id></output_format>"
    )


def draft_prompt(
    frame: str,
    tactic: str,
    parsed_claim: str,
    weakness: str,
    evidence: str,
    legacy_prompt: str,
    debate_history: str = "",
) -> str:
    evidence_block = evidence or "[blocked] Aucune preuve web — pas de chiffres inventés."
    history_block = (
        f"<debate_history>\n{debate_history}\n</debate_history>\n" if debate_history else ""
    )
    return (
        f"<persona_context>{legacy_prompt}</persona_context>\n"
        f"{history_block}"
        f"<debate_state>\n"
        f"Claim: {parsed_claim}\n"
        f"Weakness: {weakness}\n"
        f"Frame: {frame}\n"
        f"Tactic: {tactic}\n"
        f"Evidence: {evidence_block}\n"
        "</debate_state>\n"
        "<step_order>\n"
        "1. Construire l'argument selon la tactique.\n"
        "2. Intégrer les preuves fournies uniquement.\n"
        "3. Produire 3-5 phrases de brouillon interne.\n"
        "</step_order>"
    )


def character_prompt(draft: str, persona_vector: dict) -> str:
    forbidden = ", ".join(persona_vector.get("forbidden", []))
    return (
        f"<draft>{draft}</draft>\n"
        f"<persona>\n"
        f"name: {persona_vector.get('name', 'débatteur')}\n"
        f"cognitive: {persona_vector.get('cognitive')}\n"
        f"affective: {persona_vector.get('affective')}\n"
        f"rhetoric: {persona_vector.get('rhetoric')}\n"
        f"opener: {persona_vector.get('opener')}\n"
        f"concession_rate: {persona_vector.get('concession_rate', 0)}\n"
        f"forbidden: {forbidden}\n"
        "</persona>\n"
        "<step_order>\n"
        "1. Réécrire le brouillon dans cette voix.\n"
        "2. Respecter opener et tonalité affective.\n"
        "3. Ne pas dépasser le registre ONPC (clash, pas d'insulte).\n"
        "</step_order>"
    )


def polish_prompt(draft: str, sentence_max: int) -> str:
    return (
        f"<draft>{draft}</draft>\n"
        "<channel>Plateau TV français — On n'est pas couché</channel>\n"
        f"<length_limit>Maximum {sentence_max} phrases</length_limit>\n"
        "<step_order>\n"
        "1. Condenser en réplique percutante.\n"
        "2. Ajouter une punchline finale.\n"
        "3. Vérifier la limite de phrases.\n"
        "</step_order>\n"
        "<output_format>Texte à l'antenne uniquement, sans guillemets ni préfixe.</output_format>"
    )
