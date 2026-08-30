"""Oreillette spectateur : question lue à l'ouverture et en direct."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import show.runtime.llm as llm
from show.graph.show_graph import run_show
from show.guests.personas.registry import make_guest


def fake_think(model, system, user, *, temperature, max_tokens=None):
    if "SCORE" in system:
        return "CLAIM: L'IA doit être encadrée.\nWEAKNESS: Aucun critère précis.\nATTACK: argument\nSCORE: 8"
    if "TACTIC" in system:
        return "TACTIC: clash"
    if "monologue intérieur" in system:
        return "Je doute plus que je ne le montre. Mais je tiens ma ligne."
    return "Réponse simulée pour le test, cohérente avec le rôle demandé."


def test_earpiece_opening_and_live(monkeypatch):
    monkeypatch.setattr(llm, "think", fake_think)
    monkeypatch.setattr(llm, "search", lambda client, model, query: "Preuve simulée 2025.")

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


def test_live_earpiece_reaches_next_guest_prompt(monkeypatch):
    """After a live drain, the next guest listen/draft must see the spectator question."""
    captured: list[str] = []

    def capturing_think(model, system, user, *, temperature, max_tokens=None):
        captured.append(user)
        return fake_think(model, system, user, temperature=temperature, max_tokens=max_tokens)

    monkeypatch.setattr(llm, "think", capturing_think)
    monkeypatch.setattr(llm, "search", lambda client, model, query: "Preuve simulée 2025.")

    guest_a = make_guest("provocateur", "physicien", "quantique", 0.8, agent_id="guest_a")
    guest_b = make_guest("diplomate", "philosophe", "éthique", -0.6, agent_id="guest_b")

    # Opening drains the first item; the second is held for a live interjection
    # after round 1 (max_rounds=2 so conclude does not win over earpiece).
    queue = [
        "Question d'ouverture sans lien.",
        "Et si l'IA se trompe sur les peaux foncées ?",
    ]

    def poll():
        return queue.pop(0) if queue else None

    def peek():
        return len(queue) > 0

    events = []
    run_show(
        "Faut-il ralentir le déploiement de l'IA ?",
        guest_a,
        guest_b,
        max_rounds=2,
        client=None,
        enable_web_search=False,
        emit=events.append,
        poll_earpiece=poll,
        peek_earpiece=peek,
    )

    live = [e for e in events if e["type"] == "earpiece" and e["phase"] == "live"]
    assert live, "expected a live earpiece interjection"
    assert "peaux foncées" in live[0]["text"]

    guest_prompts = [
        u for u in captured
        if "peaux foncées" in u and (
            "Question du public" in u or "question du public" in u
        )
    ]
    assert guest_prompts, (
        "next guest listen/draft must include the drained spectator question"
    )


if __name__ == "__main__":
    class _MP:
        def setattr(self, obj, name, value):
            setattr(obj, name, value)

    test_earpiece_opening_and_live(_MP())
    test_live_earpiece_reaches_next_guest_prompt(_MP())
    print("OK: test_show_earpiece")
