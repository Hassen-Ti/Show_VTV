"""Topologies : chaque domaine produit un sous-graphe distinct, le show compile."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.graph.guest_subgraph import build_guest_subgraph, route_concession
from show.graph.show_graph import build_show_graph
from show.personas.registry import DOMAINS, make_guest

COMMON_TAIL = {"concede_then_refute", "draft", "voice", "deliver"}


def _node_names(compiled):
    return {n for n in compiled.get_graph().nodes if n not in ("__start__", "__end__")}


def test_each_domain_compiles_with_its_own_sequence():
    for domain, spec in DOMAINS.items():
        guest = make_guest("cerebral", domain, "spécialité", 0.5, agent_id="g")
        compiled = build_guest_subgraph(guest)
        names = _node_names(compiled)
        assert set(spec["cognitive_sequence"]) <= names, domain
        assert COMMON_TAIL <= names, domain


def test_domain_topologies_are_distinct():
    topologies = set()
    for domain in DOMAINS:
        guest = make_guest("provocateur", domain, "x", 0.0, agent_id="g")
        topologies.add(frozenset(_node_names(build_guest_subgraph(guest))))
    assert len(topologies) == len(DOMAINS)


def test_route_concession():
    assert route_concession({"turn": {"must_concede": True}}) == "concede_then_refute"
    assert route_concession({"turn": {"must_concede": False}}) == "draft"
    assert route_concession({"turn": {}}) == "draft"


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
