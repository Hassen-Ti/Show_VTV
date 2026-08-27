"""Topologies : chaque domaine / architecture produit un sous-graphe distinct, le show compile."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config.show_presets import PRESET_KEYS, SHOW_PRESETS, build_guests, get_preset
from show.graph.guest_subgraph import build_guest_subgraph, route_concession
from show.graph.show_graph import build_show_graph
from show.guests.nodes.factories import route_critic_gate, route_supervisor
from show.personas.architectures import ARCHITECTURES
from show.personas.registry import DOMAINS, make_guest

COMMON_TAIL = {"concede_then_refute", "draft", "voice", "deliver"}


def _node_names(compiled):
    return {n for n in compiled.get_graph().nodes if n not in ("__start__", "__end__")}


def test_each_domain_compiles_with_its_own_sequence():
    for domain, spec in DOMAINS.items():
        guest = make_guest("cerebral", domain, "spécialité", 0.5, agent_id="g")
        compiled = build_guest_subgraph(guest)
        names = _node_names(compiled)
        assert spec["evidence_node"] in names, domain
        assert spec["think_node"] in names, domain
        assert COMMON_TAIL <= names, domain


def test_domain_topologies_are_distinct():
    topologies = set()
    for domain in DOMAINS:
        guest = make_guest("provocateur", domain, "x", 0.0, agent_id="g")
        topologies.add(frozenset(_node_names(build_guest_subgraph(guest))))
    assert len(topologies) == len(DOMAINS)


def test_all_architectures_compile():
    """Chaque architecture publiée compile pour un domaine empirique fixe."""
    for arch_id, spec in ARCHITECTURES.items():
        guest = make_guest(
            "cerebral",
            "physicien",
            "lab",
            0.5,
            agent_id="g",
            architecture_id=arch_id,
        )
        names = _node_names(build_guest_subgraph(guest))
        assert COMMON_TAIL <= names, arch_id
        if spec.post_draft == "reflect":
            assert {"reflect", "revise_draft"} <= names
        elif spec.post_draft == "self_correct":
            assert "self_correct" in names
        elif spec.post_draft == "critic_gate":
            assert {"critic_verify", "revise_draft"} <= names
        if spec.uses_supervisor:
            assert "supervisor_route" in names
        if spec.uses_memory_first:
            assert "recall_memory" in names
        if spec.uses_plan_first:
            assert "plan" in names


def test_supervisor_routes_to_domain_workers():
    guest = make_guest(
        "diplomate",
        "economiste",
        "macro",
        -0.3,
        agent_id="g",
        architecture_id="supervisor_worker",
    )
    names = _node_names(build_guest_subgraph(guest))
    assert "supervisor_route" in names
    assert "quantify" in names  # evidence_node économiste
    assert "model_tradeoff" in names  # think_node économiste
    assert "reframe_concept" in names  # branche dialectique fixe


def test_route_concession():
    assert route_concession({"turn": {"must_concede": True}}) == "concede_then_refute"
    assert route_concession({"turn": {"must_concede": False}}) == "draft"
    assert route_concession({"turn": {}}) == "draft"


def test_route_supervisor_and_critic_gate():
    assert route_supervisor({"turn": {"worker": "dialectic"}}) == "dialectic"
    assert route_supervisor({"turn": {}}) == "evidence"
    assert route_critic_gate({"turn": {"critic_pass": True}}) == "voice"
    assert route_critic_gate({"turn": {"critic_pass": False}}) == "revise_draft"
    assert route_critic_gate({"turn": {}}) == "revise_draft"


def test_presets_build_valid_guests():
    assert set(PRESET_KEYS) == set(SHOW_PRESETS)
    for key in PRESET_KEYS:
        preset = get_preset(key)
        assert preset.key == key or (key == "" and preset.key == "")
        guest_a, guest_b = build_guests(key)
        assert guest_a.agent_id == "guest_a"
        assert guest_b.agent_id == "guest_b"
        assert guest_a.personality == preset.guest_a.personality
        assert guest_b.domain == preset.guest_b.domain
        # Les deux sous-graphes compilent.
        assert COMMON_TAIL <= _node_names(build_guest_subgraph(guest_a))
        assert COMMON_TAIL <= _node_names(build_guest_subgraph(guest_b))


def test_show_graph_compiles():
    guest_a = make_guest("provocateur", "physicien", "quantique", 0.8, agent_id="guest_a")
    guest_b = make_guest("diplomate", "philosophe", "éthique", -0.6, agent_id="guest_b")
    compiled = build_show_graph(guest_a, guest_b)
    names = _node_names(compiled)
    for expected in (
        "moderator_open",
        "moderator_allocate_floor",
        "guest_a",
        "guest_b",
        "update_shared_state",
        "moderator_interject",
        "moderator_conclude",
    ):
        assert expected in names


if __name__ == "__main__":
    test_each_domain_compiles_with_its_own_sequence()
    test_domain_topologies_are_distinct()
    test_route_concession()
    test_show_graph_compiles()
    print("OK: test_show_topology")
