"""
Test minimal : recherche web via l’API Responses OpenAI (clé dans `.env`).

Marqué `network` — sous pytest sans TTY / sans clé, le test est skippé.
Lancer en interactif : `uv run python tests/test_web_search_openai.py`
"""
from __future__ import annotations

import os
import sys

import pytest
from dotenv import load_dotenv
from openai import OpenAI

pytestmark = pytest.mark.network


def test_web_search_simple():
    if not sys.stdin.isatty():
        pytest.skip("interactive network test; run: python tests/test_web_search_openai.py")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY required for live web-search check")

    print("OPENAI_API_KEY détectée (valeur non affichée).")
    client = OpenAI(api_key=api_key)
    print("Test web search — taper 'quit' pour sortir.")

    while True:
        question = input("\nQuestion (ou quit): ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        print("Recherche en cours...")
        try:
            response = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=question,
            )
            print(response.output_text)
        except Exception as e:
            print(f"Erreur: {e}")


if __name__ == "__main__":
    test_web_search_simple()
