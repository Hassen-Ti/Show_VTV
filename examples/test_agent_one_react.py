#!/usr/bin/env python3
"""
Test de l’agent **optimiste** (`Agent_one`) avec une architecture **ReAct**
via LangChain ``create_agent`` (boucle modèle ⇄ outils sur LangGraph).

- Le **prompt système** est celui de ``Agent_one.get_system_prompt()`` (``src/agents/agent_1.py``).
- Le **modèle** ChatOpenAI est ``gpt-5-mini`` (cohérent avec les autres exemples ; distinct du ``gpt-4o``
  utilisé dans la classe legacy pour l’app PyQt).

Prérequis ::
    uv sync --extra langgraph-example
    cp .env.example .env   # OPENAI_API_KEY

Usage ::
    uv run python examples/test_agent_one_react.py
    uv run python examples/test_agent_one_react.py --topic "L'IA doit-elle encadrer les élections ?"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from agents.agent_1 import Agent_one  # noqa: E402
from utils.token_manager import token_manager  # noqa: E402

OPENAI_MODEL = "gpt-5-mini"


@tool
def internet_search(query: str) -> str:
    """Recherche Internet pour étayer le débat (remplacer par Tavily / DDGS / etc.)."""
    return f"[stub] résultats factices pour : {query[:200]}"


def optimist_system_prompt() -> str:
    """Réutilise exactement le prompt défini dans ``Agent_one``."""
    load_dotenv(ROOT / ".env")
    agent = Agent_one()
    return agent.get_system_prompt(token_manager.get_current_tokens())


def build_optimist_react_agent(system_prompt: str):
    model = ChatOpenAI(model=OPENAI_MODEL)
    return create_agent(
        model,
        [internet_search],
        system_prompt=system_prompt,
    )


def last_ai_text(messages) -> str:
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            return str(m.content)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Test Agent_one en ReAct (create_agent).")
    parser.add_argument(
        "--topic",
        default="Faut-il accélérer le déploiement de l'IA dans les hôpitaux en 2025 ?",
        help="Message utilisateur / sujet de débat.",
    )
    args = parser.parse_args()

    system_prompt = optimist_system_prompt()
    graph = build_optimist_react_agent(system_prompt)

    result = graph.invoke({"messages": [HumanMessage(content=args.topic)]})
    messages = result.get("messages", [])
    answer = last_ai_text(messages)

    print("=== Prompt système (Agent_one.get_system_prompt) ===")
    preview = system_prompt if len(system_prompt) <= 1200 else system_prompt[:1200] + "\n…"
    print(preview)
    print()
    print("=== Question ===")
    print(args.topic)
    print()
    print("=== Réponse (dernier message assistant) ===")
    print(answer or "(vide — dump brut)")
    if not answer:
        print(result)


if __name__ == "__main__":
    main()
