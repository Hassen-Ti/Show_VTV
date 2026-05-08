"""
Test du fact-checker (imports depuis `src/`).
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from agents.agent_factchecker import AgentFactChecker


def test_fact_checker():
    print("=" * 60)
    print("TEST FACT-CHECKER")
    print("=" * 60)

    checker = AgentFactChecker()
    test_statements = [
        "ChatGPT a été lancé en novembre 2022 par OpenAI",
        "Microsoft a investi 10 milliards de dollars dans OpenAI",
        "L'IA a supprimé 50 millions d'emplois en 2024",
        "GPT-4 a 1 trillion de paramètres",
        "Claude 3 d'Anthropic a été lancé en 2024",
        "90% des étudiants utilisent ChatGPT pour leurs devoirs",
    ]

    for i, statement in enumerate(test_statements, 1):
        print(f"\nTEST {i}: {statement}")
        print("-" * 50)
        fake_agent_message = f"Je pense que {statement}. C'est un fait important."
        result = checker.analyze_agent_response("Test Agent", fake_agent_message)
        display = checker.format_fact_check_display(result, f"Test {i}")
        print(display)
        input("\nEntrée pour continuer...")

    print("\nTerminé.")


if __name__ == "__main__":
    test_fact_checker()
