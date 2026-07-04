"""Algorithmes mind (purs) : dérive d'opinion, émotions, tension, concession."""

import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.mind import (
    appraise,
    compute_tension,
    decay,
    effective_sentence_max,
    effective_voice_temperature,
    revise_stance,
    should_concede,
    update_conviction,
)
from show.personas.registry import make_guest
from show.state import initial_mind


def _guest(**overrides):
    guest = make_guest("diplomate", "philosophe", "éthique", -0.6, agent_id="g")
    return replace(guest, **overrides) if overrides else guest


def _entry(tactic, role="guest"):
    return {
        "round": 1, "speaker": "x", "speaker_name": "X", "role": role,
        "text": "…", "tactic": tactic, "evidence_used": False,
    }


def test_revise_stance_moves_toward_opponent():
    persona = _guest()
    mind = initial_mind(persona)
    revised = revise_stance(mind, persona, opponent_stance=0.8, persuasion=0.9)
    assert revised["stance"] > mind["stance"]
    assert -1.0 <= revised["stance"] <= 1.0


def test_revise_stance_stubborn_does_not_move():
    persona = _guest(stubbornness=1.0)
    mind = initial_mind(persona)
    revised = revise_stance(mind, persona, opponent_stance=0.8, persuasion=1.0)
    assert revised["stance"] == mind["stance"]


def test_revise_stance_capped_by_gap():
    persona = _guest(stubbornness=0.0)
    mind = dict(initial_mind(persona))
    mind["stance"] = 0.79
    mind["conviction"] = 0.0
    revised = revise_stance(mind, persona, opponent_stance=0.8, persuasion=1.0)
    assert abs(revised["stance"] - 0.8) < 1e-9  # ne dépasse jamais l'adversaire


def test_update_conviction_bounds():
    persona = _guest()
    mind = dict(initial_mind(persona))
    mind["conviction"] = 0.12
    eroded = update_conviction(mind, persuasion=1.0, countered=False)
    assert eroded["conviction"] >= 0.1
    mind["conviction"] = 0.99
    boosted = update_conviction(mind, persuasion=0.0, countered=True)
    assert boosted["conviction"] <= 1.0


def test_should_concede_threshold_and_trait():
    persona = _guest()  # concession_rate 0.35
    assert should_concede(persuasion=0.9, persona=persona, rand=0.99)
    assert should_concede(persuasion=0.1, persona=persona, rand=0.1)
    assert not should_concede(persuasion=0.1, persona=persona, rand=0.99)


def test_appraise_personal_attack_heats_up():
    persona = _guest()
    mind = initial_mind(persona)
    heated = appraise(mind, persona, "attacked_personal")
    assert heated["arousal"] > mind["arousal"]
    assert heated["valence"] < mind["valence"]


def test_decay_cools_down_and_recovers_valence():
    persona = _guest()
    mind = dict(initial_mind(persona))
    mind["arousal"] = 0.8
    mind["valence"] = -0.5
    cooled = decay(mind, persona)
    assert cooled["arousal"] < 0.8
    assert cooled["valence"] > -0.5  # remonte vers la baseline (0.3)


def test_arousal_modulates_voice_and_length():
    persona = _guest()
    hot = dict(initial_mind(persona))
    hot["arousal"] = 0.9
    cold = dict(initial_mind(persona))
    cold["arousal"] = 0.1
    assert effective_voice_temperature(hot, persona) > effective_voice_temperature(cold, persona)
    assert effective_sentence_max(hot, persona, 0.75) == persona.sentence_max - 1
    assert effective_sentence_max(cold, persona, 0.75) == persona.sentence_max


def test_compute_tension_attack_density():
    persona = _guest()
    minds = {"a": initial_mind(persona), "b": initial_mind(persona)}
    calm = compute_tension(minds, [_entry("pivot"), _entry("pivot")])
    heated = compute_tension(minds, [_entry("clash"), _entry("moral_attack")])
    assert heated > calm
    assert 0.0 <= calm <= heated <= 1.0


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
    print("OK: test_show_mind")
