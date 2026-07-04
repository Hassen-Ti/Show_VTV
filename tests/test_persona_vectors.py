"""Tests schéma persona_vector ONPC."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config.debate_graph import (
    PERSONA_OPTIMISTE,
    PERSONA_SCEPTIQUE,
    TACTICS,
    get_persona_vector,
    validate_persona_vector,
)


def test_builtin_persona_vectors_valid():
    assert validate_persona_vector(PERSONA_OPTIMISTE) == []
    assert validate_persona_vector(PERSONA_SCEPTIQUE) == []


def test_agent_side_vectors():
    one = get_persona_vector("optimiste")
    two = get_persona_vector("sceptique")
    assert validate_persona_vector(one) == []
    assert validate_persona_vector(two) == []
    assert one["affective"] == "triumphant"
    assert two["affective"] == "indignant"


def test_tactics_subset():
    for persona in (PERSONA_OPTIMISTE, PERSONA_SCEPTIQUE):
        for tactic in persona["tactics"]:
            assert tactic in TACTICS


if __name__ == "__main__":
    test_builtin_persona_vectors_valid()
    test_agent_side_vectors()
    test_tactics_subset()
    print("OK: test_persona_vectors")
