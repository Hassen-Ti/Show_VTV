"""Smoke test : un show complet (1 round) avec LLM mocké, sans réseau."""

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


def test_full_show_one_round(monkeypatch):
    monkeypatch.setattr(show.llm, "think", fake_think)
    monkeypatch.setattr(show.llm, "search", lambda client, model, query: "Preuve simulée 2025.")

    guest_a = make_guest("provocateur", "physicien", "quantique", 0.8, agent_id="guest_a")
    guest_b = make_guest("diplomate", "philosophe", "éthique", -0.6, agent_id="guest_b")

    events = []
    result = run_show(
        "Faut-il ralentir le déploiement de l'IA ?",
        guest_a,
        guest_b,
        max_rounds=1,
        client=None,          # pas de réseau : web search désactivé
        enable_web_search=False,
        emit=events.append,
    )

    # Transcript : intro + 2 passages de parole + 2 répliques invités + conclusion.
    roles = [(e["role"], e["speaker"]) for e in result["transcript"]]
    assert roles.count(("guest", "guest_a")) == 1
    assert roles.count(("guest", "guest_b")) == 1
    assert sum(1 for r, _ in roles if r == "moderator") == 4

    # Les deux invités ont parlé avec une tactique autorisée par leur persona.
    guest_entries = {e["speaker"]: e for e in result["transcript"] if e["role"] == "guest"}
    assert guest_entries["guest_a"]["tactic"] in guest_a.tactics
    assert guest_entries["guest_b"]["tactic"] in guest_b.tactics + ("concede_then_refute",)

    # Shared state : stances historisées, dérive du diplomate vers l'adversaire.
    history_b = result["stance_history"]["guest_b"]
    assert len(history_b) == 3  # initiale + 2 mises à jour (une par tour)
    assert history_b[-1] > history_b[0]  # persuasion 0.8 → il a bougé

    # Conscience agentique : monologue intérieur privé, jamais dans le transcript.
    for agent_id in ("guest_a", "guest_b"):
        monologue = result["minds"][agent_id]["inner_monologue"]
        assert monologue
        assert all(monologue not in e["text"] for e in result["transcript"])

    # Événements émis pour le runner/UI.
    kinds = {e["type"] for e in events}
    assert {"moderator", "turn", "inner_monologue", "stance_update", "step"} <= kinds

    from show.runtime.events import validate_emit_event

    for event in events:
        validate_emit_event(event)

    # Les deux minds restent présentes après deltas partiels (merge_minds).
    assert set(result["minds"]) == {"guest_a", "guest_b"}


if __name__ == "__main__":
    class _MP:
        def setattr(self, obj, name, value):
            setattr(obj, name, value)

    test_full_show_one_round(_MP())
    print("OK: test_show_smoke")
