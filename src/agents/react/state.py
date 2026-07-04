"""État partagé du graphe débatteur ONPC."""

from __future__ import annotations

from typing import Any, TypedDict


class DebateTurnState(TypedDict, total=False):
    topic: str
    opponent_last: str
    debate_history: str
    persona_vector: dict[str, Any]
    system_prompt_legacy: str
    enable_web_search: bool
    is_round_one: bool
    parsed_claim: str
    weakness: str
    frame: str
    needs_evidence: bool
    evidence_query: str
    evidence: str
    tactic: str
    draft: str
    final: str
    current_step: str
    delivery_model: str
    delivery_max_tokens: int


def extract_turn_inputs(user_input: str) -> tuple[str, str, bool]:
    """Extrait historique, dernière réplique adverse, et indicateur round 1."""
    marker = "🎬 HISTORIQUE DU DÉBAT"
    instruction_suffix = "en tenant compte de cet historique!"
    if marker in user_input:
        before, _, after = user_input.partition("🎯 RÉPONDEZ MAINTENANT")
        history = before.strip()
        opponent = after.strip()
        if opponent.startswith(instruction_suffix):
            opponent = opponent[len(instruction_suffix):].strip()
        is_round_one = "ADVERSAIRE" not in history
        return history, opponent or user_input.strip(), is_round_one
    return "", user_input.strip(), True


def initial_state(
    user_input: str,
    *,
    topic: str,
    persona_vector: dict,
    system_prompt_legacy: str,
    enable_web_search: bool,
    delivery_model: str,
    delivery_max_tokens: int,
) -> DebateTurnState:
    history, opponent_last, is_round_one = extract_turn_inputs(user_input)
    return DebateTurnState(
        topic=topic or opponent_last,
        opponent_last=opponent_last,
        debate_history=history,
        persona_vector=persona_vector,
        system_prompt_legacy=system_prompt_legacy,
        enable_web_search=enable_web_search,
        is_round_one=is_round_one,
        parsed_claim="",
        weakness="",
        frame="",
        needs_evidence=False,
        evidence_query="",
        evidence="",
        tactic="",
        draft="",
        final="",
        current_step="",
        delivery_model=delivery_model,
        delivery_max_tokens=delivery_max_tokens,
    )
