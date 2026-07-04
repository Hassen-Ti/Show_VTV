"""Registre personas : matrice personnalité × domaine, validation stricte."""

import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.personas.registry import DOMAINS, PERSONALITIES, make_guest
from show.personas.vector import validate


def test_all_combinations_are_valid():
    for personality in PERSONALITIES:
        for domain in DOMAINS:
            guest = make_guest(personality, domain, "spécialité test", 0.5, agent_id="g")
            assert guest.personality == personality
            assert guest.domain == domain
            assert guest.cognitive_sequence[0] == "listen"
            assert guest.cognitive_sequence[-1] == "strategize"


def test_unknown_personality_raises():
    with pytest.raises(ValueError, match="personnalité inconnue"):
        make_guest("troll", "physicien", "x", 0.0, agent_id="g")


def test_unknown_domain_raises():
    with pytest.raises(ValueError, match="domaine inconnu"):
        make_guest("provocateur", "astrologue", "x", 0.0, agent_id="g")


def test_domains_have_distinct_cognitive_sequences():
    sequences = {tuple(d["cognitive_sequence"]) for d in DOMAINS.values()}
    assert len(sequences) == len(DOMAINS)


def test_validate_rejects_out_of_range_stance():
    guest = make_guest("cerebral", "historien", "x", 0.5, agent_id="g")
    broken = replace(guest, initial_stance=2.0)
    with pytest.raises(ValueError, match="initial_stance"):
        validate(broken)


def test_validate_rejects_unknown_tactic():
    guest = make_guest("cerebral", "historien", "x", 0.5, agent_id="g")
    broken = replace(guest, tactics=("hypnose",))
    with pytest.raises(ValueError, match="tactiques inconnues"):
        validate(broken)


if __name__ == "__main__":
    test_all_combinations_are_valid()
    test_domains_have_distinct_cognitive_sequences()
    print("OK: test_show_registry")
