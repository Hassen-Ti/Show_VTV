"""Tests routing et état du graphe débatteur."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.react.routing import route_after_frame
from agents.react.state import extract_turn_inputs, initial_state
from config.settings import OPENAI_MODEL


def test_route_skips_search_when_disabled():
    state = {
        "enable_web_search": False,
        "needs_evidence": True,
        "evidence_query": "stat IA 2025",
    }
    assert route_after_frame(state) == "select_tactic"


def test_route_goes_to_search_when_evidence_needed():
    state = {
        "enable_web_search": True,
        "is_round_one": False,
        "needs_evidence": True,
        "evidence_query": "chômage IA France",
    }
    assert route_after_frame(state) == "search_web"


def test_route_skips_search_without_query():
    state = {
        "enable_web_search": True,
        "needs_evidence": True,
        "evidence_query": "",
    }
    assert route_after_frame(state) == "select_tactic"


def test_extract_turn_inputs_round_one():
    history, opponent, is_round_one = extract_turn_inputs("L'IA va-t-elle détruire l'emploi?")
    assert history == ""
    assert "emploi" in opponent
    assert is_round_one is True


def test_extract_turn_inputs_with_history():
    text = (
        "🎬 HISTORIQUE DU DÉBAT (pour référence):\n"
        "[Round 1] 🔥 ADVERSAIRE: Premier argument\n\n"
        "🎯 RÉPONDEZ MAINTENANT en tenant compte de cet historique!\n"
        "Votre adversaire ment sur les chiffres."
    )
    history, opponent, is_round_one = extract_turn_inputs(text)
    assert "HISTORIQUE" in history
    assert "chiffres" in opponent
    assert "historique" not in opponent  # suffixe d'instruction retiré
    assert is_round_one is False


def test_initial_state_sets_persona():
    state = initial_state(
        "Sujet test",
        topic="Sujet test",
        persona_vector={"name": "Test"},
        system_prompt_legacy="legacy",
        enable_web_search=True,
        delivery_model=OPENAI_MODEL,
        delivery_max_tokens=150,
    )
    assert state["topic"] == "Sujet test"
    assert state["persona_vector"]["name"] == "Test"
    assert state["is_round_one"] is True


if __name__ == "__main__":
    test_route_skips_search_when_disabled()
    test_route_goes_to_search_when_evidence_needed()
    test_route_skips_search_without_query()
    test_extract_turn_inputs_round_one()
    test_extract_turn_inputs_with_history()
    test_initial_state_sets_persona()
    print("OK: test_debate_graph_routing")
