"""Tests utilitaires de parsing des nœuds."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.react.nodes.common import first_allowed_tactic, parse_labeled_lines, parse_yes_no


def test_parse_labeled_lines():
    text = "CLAIM: L'IA crée des emplois\nWEAKNESS: pas de preuve récente"
    parsed = parse_labeled_lines(text, ["CLAIM", "WEAKNESS"])
    assert parsed["claim"] == "L'IA crée des emplois"
    assert "preuve" in parsed["weakness"]


def test_parse_yes_no():
    assert parse_yes_no("oui") is True
    assert parse_yes_no("non") is False


def test_first_allowed_tactic():
    allowed = ["clash", "pivot_future", "dismiss_fear"]
    assert first_allowed_tactic("TACTIC: pivot_future", allowed, "clash") == "pivot_future"
    assert first_allowed_tactic("inconnu", allowed, "clash") == "clash"


if __name__ == "__main__":
    test_parse_labeled_lines()
    test_parse_yes_no()
    test_first_allowed_tactic()
    print("OK: test_debate_graph_unit")
