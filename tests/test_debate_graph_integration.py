"""Integration manuelle — nécessite OPENAI_API_KEY."""

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def test_one_debate_turn_live():
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: no OPENAI_API_KEY")
        return
    from openai import OpenAI

    from agents.react.graph import run_debate_turn
    from config.debate_graph import get_persona_vector
    from config.settings import OPENAI_MODEL

    client = OpenAI()
    steps: list[str] = []

    start = time.perf_counter()
    result = run_debate_turn(
        client=client,
        model=OPENAI_MODEL,
        temperature=1.1,
        max_tokens=150,
        system_prompt="Tu es un débatteur optimiste TV.",
        user_input="L'IA va-t-elle détruire l'emploi en 2025?",
        persona_vector=get_persona_vector("optimiste"),
        enable_web_search=True,
        step_callback=steps.append,
    )
    elapsed = time.perf_counter() - start

    assert result and not result.startswith("Error:")
    assert len(result) > 20
    print(f"FINAL ({elapsed:.1f}s):", result[:200])
    print("STEPS:", len(steps))


if __name__ == "__main__":
    test_one_debate_turn_live()
    print("OK: integration (or SKIP)")
