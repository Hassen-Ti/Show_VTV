#!/usr/bin/env python3
"""
Un seul agent (LangChain ``create_agent`` sur LangGraph ; remplace l’ancien ``create_react_agent`` déprécié, cf. migration LangGraph v1).
LLM OpenAI + outil de recherche, boucle agent ⇄ tools jusqu'à réponse finale.

Modèle API : ``gpt-5-mini`` (alias officiel « GPT-5 mini »).
Doc : https://developers.openai.com/api/docs/models/gpt-5-mini

Usage ::
    uv run python examples/langgraph_debate_architecture.py

Sorties dans ``examples/`` :
  - ``langgraph_single_agent_react.mmd`` (source Mermaid)
  - ``langgraph_single_agent_react.jpg`` (image du graphe)

Environnement ::
    uv sync --extra langgraph-example
    uv run python examples/langgraph_debate_architecture.py

Migration : https://docs.langchain.com/oss/python/migrate/langgraph-v1
"""

from __future__ import annotations

import argparse
import sys
from io import BytesIO
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

ROOT = Path(__file__).resolve().parents[1]

OPENAI_MODEL = "gpt-5-mini"


@tool
def internet_search(query: str) -> str:
    """Recherche web : branche une vraie API (Tavily, SerpAPI, DDGS, etc.)."""
    return f"[stub] synthèse fictive pour : {query[:160]}"


def build_openai_chat_model() -> ChatOpenAI:
    return ChatOpenAI(model=OPENAI_MODEL)


def build_single_agent_graph():
    """Graphe compilé : ``create_agent`` (middleware ReAct / tools sur LangGraph)."""
    model = build_openai_chat_model()
    system_prompt = """Tu raisonnes au format ReAct : réfléchis, puis appelle internet_search
si tu as besoin de faits récents ou vérifiables, puis conclus en français."""
    return create_agent(
        model,
        [internet_search],
        system_prompt=system_prompt,
    )


def export_mermaid(compiled, out_path: Path, *, xray: bool = True) -> None:
    mermaid = compiled.get_graph(xray=xray).draw_mermaid()
    out_path.write_text(mermaid, encoding="utf-8")


def export_graph_jpg(compiled, out_jpg: Path, *, xray: bool = True, quality: int = 92) -> None:
    """PNG via ``draw_mermaid_png`` (API Mermaid), puis conversion JPEG avec Pillow."""
    try:
        from PIL import Image
    except ImportError as e:
        raise RuntimeError(
            "Pour générer le JPG : pip install pillow"
        ) from e

    png_bytes = compiled.get_graph(xray=xray).draw_mermaid_png()
    img = Image.open(BytesIO(png_bytes)).convert("RGB")
    img.save(out_jpg, format="JPEG", quality=quality, optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-xray",
        action="store_true",
        help="Diagramme sans détail des nœuds internes.",
    )
    parser.add_argument(
        "--no-jpg",
        action="store_true",
        help="Ne pas générer le fichier .jpg (Mermaid uniquement).",
    )
    args = parser.parse_args()

    xray = not args.no_xray
    app = build_single_agent_graph()

    out_mmd = ROOT / "examples" / "langgraph_single_agent_react.mmd"
    out_jpg = ROOT / "examples" / "langgraph_single_agent_react.jpg"

    export_mermaid(app, out_mmd, xray=xray)
    print(f"Modèle OpenAI : {OPENAI_MODEL}")
    print(f"Mermaid -> {out_mmd}")

    if not args.no_jpg:
        try:
            export_graph_jpg(app, out_jpg, xray=xray)
            print(f"Image JPG -> {out_jpg}")
        except Exception as e:
            print(f"Avertissement JPG : {e}", file=sys.stderr)

    print()
    print("=== Mermaid ===")
    print(app.get_graph(xray=xray).draw_mermaid())


if __name__ == "__main__":
    main()
