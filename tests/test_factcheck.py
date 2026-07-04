"""
Test du fact-checker (imports depuis `src/`).

Par défaut : exécution non interactive avec assertions (exit 0/1).
Usage interactif : ``uv run python tests/test_factcheck.py --interactive``
"""
import argparse
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from agents.agent_factchecker import AgentFactChecker

# (statement, expected verdict prefix)
CASES = [
    ("ChatGPT a été lancé en novembre 2022 par OpenAI", "💬"),
    ("Microsoft a investi 10 milliards de dollars dans OpenAI", "📊"),
    ("L'IA a supprimé 50 millions d'emplois en 2024", "📊"),
    ("GPT-4 a 1 trillion de paramètres", "💬"),
    ("Claude 3 d'Anthropic a été lancé en 2024", "💬"),
    ("90% des étudiants utilisent ChatGPT pour leurs devoirs", "📊"),
]


def run_fact_checker(*, interactive: bool = False, verbose: bool = True) -> int:
    if verbose:
        print("=" * 60)
        print("TEST FACT-CHECKER")
        print("=" * 60)

    checker = AgentFactChecker()
    failures = 0

    for i, (statement, expected_verdict) in enumerate(CASES, 1):
        if verbose:
            print(f"\nTEST {i}: {statement}")
            print("-" * 50)

        fake_agent_message = f"Je pense que {statement}. C'est un fait important."
        result = checker.analyze_agent_response("Test Agent", fake_agent_message)
        display = checker.format_fact_check_display(result, f"Test {i}")

        if verbose:
            print(display)

        verdict = result.get("verdict", "")
        if not verdict.startswith(expected_verdict):
            failures += 1
            print(
                f"FAIL test {i}: expected verdict starting with {expected_verdict!r}, "
                f"got {verdict!r}",
                file=sys.stderr,
            )

        if interactive:
            input("\nEntrée pour continuer...")

    if verbose:
        print(f"\n{'Échec' if failures else 'Terminé'} — {len(CASES) - failures}/{len(CASES)} OK.")

    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Test local du fact-checker (sans appels API).")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Pause entre chaque cas (comportement manuel d'origine).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Sortie minimale ; utile en CI.",
    )
    args = parser.parse_args()
    return run_fact_checker(interactive=args.interactive, verbose=not args.quiet)


if __name__ == "__main__":
    sys.exit(main())
