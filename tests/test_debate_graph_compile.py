"""Smoke: graphe LangGraph compile et structure des nœuds."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.react.graph import build_debate_graph, draw_debate_graph_mermaid


def test_graph_compiles():
    compiled = build_debate_graph()
    assert compiled is not None


def test_mermaid_contains_all_nodes():
    mermaid = draw_debate_graph_mermaid()
    for node in (
        "parse_opponent",
        "choose_frame",
        "search_web",
        "select_tactic",
        "draft_argument",
        "apply_character",
        "polish_onpc",
    ):
        assert node in mermaid


if __name__ == "__main__":
    test_graph_compiles()
    test_mermaid_contains_all_nodes()
    print("OK: test_debate_graph_compile")
