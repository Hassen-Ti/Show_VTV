"""Registre personas : matrice personnalité × domaine, validation stricte."""

import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.guests.nodes import NODE_REGISTRY
from show.personas.architectures import ARCHITECTURES, PERSONALITY_ARCHITECTURE
from show.personas.registry import DOMAINS, PERSONALITIES, domain_worker_nodes, make_guest
from show.personas.vector import COGNITIVE_NODES, validate


def test_all_combinations_are_valid():
    for personality in PERSONALITIES:
        for domain in DOMAINS:
            guest = make_guest(personality, domain, "spécialité test", 0.5, agent_id="g")
            assert guest.personality == personality
            assert guest.domain == domain
            assert guest.cognitive_sequence[0] in ("listen", "recall_memory")
            assert guest.cognitive_sequence[-1] == "strategize"


def test_cognitive_sequence_uses_domain_workers():
    """Hors supervisor, la séquence embarque les nœuds preuve/pensée du domaine."""
    for domain, spec in DOMAINS.items():
        guest = make_guest("provocateur", domain, "x", 0.0, agent_id="g")
        evidence, think = domain_worker_nodes(domain)
        assert evidence == spec["evidence_node"]
        assert think == spec["think_node"]
        # ReAct (provocateur) remplace verify_facts / hypothesize par les nœuds domaine.
        assert evidence in guest.cognitive_sequence
        assert think in guest.cognitive_sequence


def test_unknown_personality_raises():
    with pytest.raises(ValueError, match="personnalité inconnue"):
        make_guest("troll", "physicien", "x", 0.0, agent_id="g")


def test_unknown_domain_raises():
    with pytest.raises(ValueError, match="domaine inconnu"):
        make_guest("provocateur", "astrologue", "x", 0.0, agent_id="g")


def test_unknown_architecture_raises():
    with pytest.raises(ValueError, match="architecture inconnue"):
        make_guest(
            "cerebral",
            "historien",
            "x",
            0.0,
            agent_id="g",
            architecture_id="does_not_exist",
        )


def test_architecture_override():
    guest = make_guest(
        "provocateur",
        "physicien",
        "x",
        0.5,
        agent_id="g",
        architecture_id="reflexion",
    )
    assert guest.architecture_id == "reflexion"
    assert guest.cognitive_sequence[0] == "listen"
    assert "verify_facts" in guest.cognitive_sequence or "hypothesize" in guest.cognitive_sequence


def test_domains_have_evidence_styles():
    styles = {d["evidence_style"] for d in DOMAINS.values()}
    assert len(styles) == len(DOMAINS)


def test_personalities_have_architectures():
    for p in PERSONALITIES.values():
        assert p["architecture_id"] in ARCHITECTURES


def test_personality_architecture_table_matches_registry():
    """``PERSONALITY_ARCHITECTURE`` reste synchronisé avec ``PERSONALITIES``."""
    assert set(PERSONALITY_ARCHITECTURE) == set(PERSONALITIES)
    for personality, arch in PERSONALITY_ARCHITECTURE.items():
        assert PERSONALITIES[personality]["architecture_id"] == arch


def test_node_registry_covers_cognitive_nodes():
    missing = COGNITIVE_NODES - set(NODE_REGISTRY)
    assert not missing, f"NODE_REGISTRY manque: {sorted(missing)}"


def test_domain_worker_nodes_unknown_raises():
    with pytest.raises(ValueError, match="domaine inconnu"):
        domain_worker_nodes("astrologue")


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
    test_personalities_have_architectures()
    print("OK: test_show_registry")
