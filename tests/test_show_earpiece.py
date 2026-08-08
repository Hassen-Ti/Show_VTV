"""Oreillette spectateur : question lue à l'ouverture et en direct."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import show.llm
from show.graph.show_graph import run_show
from show.personas.registry import make_guest


def fake_think(model, system, user, *, temperature, max_tokens=None):
    if "SCORE" in system:
        return "CLAIM: L'IA doit être encadrée.\nWEAKNESS: Aucun critère précis.\nATTACK: argument\nSCORE: 8"
    if "TACTIC" in system:
        return "TACTIC: clash"
    if "monologue intérieur" in system:
        return "Je doute plus que je ne le montre. Mais je tiens ma ligne."
    return "Réponse simulée pour le test, cohérente avec le rôle demandé."


def test_earpiece_opening_and_live(monkeypatch):
    monkeypatch.setattr(show.llm, "think", fake_think)
    monkeypatch.setattr(show.llm, "search", lambda client, model, query: "Preuve simulée 2025.")

    guest_a = make_guest("provocateur", "physicien", "quantique", 0.8, agent_id="guest_a")
    guest_b = make_guest("diplomate", "philosophe", "éthique", -0.6, agent_id="guest_b")

    queue = ["Et si l'IA se trompe sur les peaux foncées ?"]

    def poll():
        return queue.pop(0) if queue else None

    def peek():
        return len(queue) > 0

    events = []
    run_show(
        "Faut-il ralentir le déploiement de l'IA ?",
        guest_a,
        guest_b,
        max_rounds=1,
        client=None,
        enable_web_search=False,
        emit=events.append,
        poll_earpiece=poll,
        peek_earpiece=peek,
    )

    earpiece_events = [e for e in events if e["type"] == "earpiece"]
    assert len(earpiece_events) >= 1
    assert earpiece_events[0]["phase"] == "opening"
    assert "peaux foncées" in earpiece_events[0]["text"]


if __name__ == "__main__":
    class _MP:
        def setattr(self, obj, name, value):
            setattr(obj, name, value)

    test_earpiece_opening_and_live(_MP())
    print("OK: test_show_earpiece")
