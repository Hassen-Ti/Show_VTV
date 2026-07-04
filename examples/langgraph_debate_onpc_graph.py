#!/usr/bin/env python3
"""
Graphe débatteur ONPC — export Mermaid (LangGraph StateGraph).

Réf. : https://github.com/langchain-ai/langgraph
Doc  : https://docs.langchain.com/oss/python/langgraph/use-graph-api

Usage ::
    uv run python examples/langgraph_debate_onpc_graph.py

Sortie ::
    examples/langgraph_debate_onpc.mmd
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.react.graph import draw_debate_graph_mermaid


def main() -> None:
    out = ROOT / "examples" / "langgraph_debate_onpc.mmd"
    mermaid = draw_debate_graph_mermaid(xray=True)
    out.write_text(mermaid, encoding="utf-8")
    print(f"Mermaid -> {out}")
    print()
    print(mermaid)


if __name__ == "__main__":
    main()
