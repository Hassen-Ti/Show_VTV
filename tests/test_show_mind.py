"""Algorithmes mind (purs) : dérive d'opinion, émotions, tension, concession, persistance."""

import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.memory.mind import (
    appraise,
    compute_tension,
    decay,
    effective_sentence_max,
    effective_voice_temperature,
    revise_stance,
    should_concede,
    update_conviction,
)
from show.memory.state import (
    initial_show_state,
    seed_minds_from_prior,
    snapshot_minds,
    initial_mind,
)
from show.memory.update import make_update_shared_state
from show.guests.personas.registry import make_guest
from show.runtime.context import ShowContext


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


def test_revise_stance_zero_persuasion_and_same_stance():
    persona = _guest(stubbornness=0.0)
    mind = dict(initial_mind(persona))
    mind["conviction"] = 0.0
    unchanged = revise_stance(mind, persona, opponent_stance=0.9, persuasion=0.0)
    assert unchanged["stance"] == mind["stance"]
    same = revise_stance(mind, persona, opponent_stance=mind["stance"], persuasion=1.0)
    assert same["stance"] == mind["stance"]


def test_revise_stance_clamps_out_of_range_persuasion():
    persona = _guest(stubbornness=0.0)
    mind = dict(initial_mind(persona))
    mind["conviction"] = 0.0
    # persuasion négative → traitée comme 0
    neg = revise_stance(mind, persona, opponent_stance=0.9, persuasion=-5.0)
    assert neg["stance"] == mind["stance"]
    # persuasion > 1 ne doit pas dépasser le comportement à persuasion=1
    hi = revise_stance(mind, persona, opponent_stance=0.9, persuasion=50.0)
    one = revise_stance(mind, persona, opponent_stance=0.9, persuasion=1.0)
    assert abs(hi["stance"] - one["stance"]) < 1e-12


def test_revise_stance_does_not_mutate_input():
    persona = _guest()
    mind = initial_mind(persona)
    beliefs = mind["beliefs"]
    revise_stance(mind, persona, opponent_stance=0.8, persuasion=0.9)
    assert mind["beliefs"] is beliefs
    assert mind["stance"] == persona.initial_stance


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


def test_appraise_unknown_event_is_noop():
    persona = _guest()
    mind = initial_mind(persona)
    same = appraise(mind, persona, "not_a_real_event")
    assert same["arousal"] == mind["arousal"]
    assert same["valence"] == mind["valence"]


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


def test_effective_sentence_max_never_below_one():
    persona = _guest(sentence_max=1)
    hot = dict(initial_mind(persona))
    hot["arousal"] = 1.0
    assert effective_sentence_max(hot, persona, 0.5) == 1


def test_compute_tension_attack_density():
    persona = _guest()
    minds = {"a": initial_mind(persona), "b": initial_mind(persona)}
    calm = compute_tension(minds, [_entry("pivot"), _entry("pivot")])
    heated = compute_tension(minds, [_entry("clash"), _entry("moral_attack")])
    assert heated > calm
    assert 0.0 <= calm <= heated <= 1.0


def test_compute_tension_empty_minds_and_no_guest_entries():
    assert compute_tension({}, []) == 0.0
    assert compute_tension(None, None) == 0.0  # type: ignore[arg-type]
    # Uniquement modérateur → densité d'attaque nulle ; minds vides → arousal 0
    assert compute_tension({}, [_entry("clash", role="moderator")]) == 0.0
    persona = _guest()
    minds = {"a": dict(initial_mind(persona), arousal=0.0)}
    # Invités calmes + pas d'attaque
    t = compute_tension(minds, [_entry("pivot"), _entry("clash", role="moderator")])
    assert t == 0.0


def test_snapshot_and_seed_minds_inter_episode():
    a = _guest(agent_id="a")
    b = make_guest("diplomate", "philosophe", "éthique", 0.4, agent_id="b")
    mind_a = dict(initial_mind(a))
    mind_a["stance"] = 0.55
    mind_a["conviction"] = 0.8
    mind_a["beliefs"] = ["fait X"]
    mind_a["grudges"] = ["attaque Y"]
    mind_a["arousal"] = 0.95
    mind_a["valence"] = -0.9
    mind_a["inner_monologue"] = "secret"
    prior = snapshot_minds({"a": mind_a, "ghost": initial_mind(a)})
    # mutation du prior ne doit pas toucher le snapshot
    mind_a["beliefs"].append("mut")
    assert prior["a"]["beliefs"] == ["fait X"]

    seeded = seed_minds_from_prior([a, b], prior)
    assert seeded["a"]["stance"] == 0.55
    assert seeded["a"]["conviction"] == 0.8
    assert seeded["a"]["beliefs"] == ["fait X"]
    assert seeded["a"]["grudges"] == ["attaque Y"]
    assert seeded["a"]["arousal"] == 0.2
    assert seeded["a"]["valence"] == a.affective_baseline
    assert seeded["a"]["inner_monologue"] == ""
    assert seeded["a"].get("carried_over") is True
    # b absent du prior → mind fraîche
    assert seeded["b"]["stance"] == b.initial_stance
    assert "carried_over" not in seeded["b"]


def test_initial_show_state_with_prior_minds():
    a = _guest(agent_id="a")
    b = make_guest("diplomate", "philosophe", "éthique", 0.2, agent_id="b")
    prior = snapshot_minds({"a": dict(initial_mind(a), stance=0.33, conviction=0.7)})
    state = initial_show_state("Sujet", [a, b], max_rounds=3, prior_minds=prior)
    assert state["minds"]["a"]["stance"] == 0.33
    assert state["stance_history"]["a"] == [0.33]
    assert state["stance_history"]["b"] == [b.initial_stance]
    assert state["tension"] == 0.0


def test_update_shared_state_decay_and_history():
    a = make_guest("diplomate", "philosophe", "éthique", -0.5, agent_id="a")
    b = make_guest("diplomate", "philosophe", "éthique", 0.5, agent_id="b")
    minds = {
        "a": dict(initial_mind(a), arousal=0.8, stance=-0.5),
        "b": dict(initial_mind(b), arousal=0.8, stance=0.5),
    }
    state = {
        "round": 1,
        "turn_index": 2,  # round complete
        "minds": minds,
        "transcript": [
            _entry("clash") | {"round": 1, "speaker": "a"},
            _entry("pivot") | {"round": 1, "speaker": "b"},
        ],
        "stance_history": {"a": [-0.5], "b": [0.5]},
    }
    events = []
    runtime = SimpleNamespace(context=ShowContext(emit=events.append))
    node = make_update_shared_state(a, b)
    out = node(state, runtime)
    assert out["minds"]["a"]["arousal"] < 0.8
    assert out["minds"]["b"]["arousal"] < 0.8
    assert out["stance_history"]["a"] == [-0.5, out["minds"]["a"]["stance"]]
    assert 0.0 <= out["tension"] <= 1.0
    assert events and events[0]["type"] == "stance_update"


def test_update_shared_state_missing_mind_and_empty_history():
    a = make_guest("diplomate", "philosophe", "éthique", -0.5, agent_id="a")
    b = make_guest("diplomate", "philosophe", "éthique", 0.5, agent_id="b")
    # Seul a est présent ; pas de stance_history ; turn_index impair → pas de decay
    state = {
        "round": 0,
        "turn_index": 1,
        "minds": {"a": dict(initial_mind(a), arousal=0.9)},
        "transcript": [],
    }
    runtime = SimpleNamespace(context=ShowContext())
    out = make_update_shared_state(a, b)(state, runtime)
    assert out["minds"]["a"]["arousal"] == 0.9  # pas de decay
    assert "b" not in out["minds"]
    assert out["stance_history"]["a"] == [out["minds"]["a"]["stance"]]
    assert out["tension"] == compute_tension(out["minds"], [])


def test_mind_traits_protocol_accepts_simple_namespace():
    """memory ne dépend plus de PersonaVector — un duck-type suffit."""
    traits = SimpleNamespace(
        agent_id="x",
        stubbornness=0.5,
        concession_rate=0.2,
        arousal_gain=0.4,
        affective_baseline=0.1,
        temperature_voice=1.0,
        sentence_max=3,
        initial_stance=0.3,
        initial_conviction=0.7,
    )
    mind = initial_mind(traits)
    assert mind["stance"] == 0.3
    assert mind["conviction"] == 0.7
    revised = revise_stance(mind, traits, opponent_stance=-0.5, persuasion=0.8)
    assert revised["stance"] < mind["stance"]
    from show.memory.traits import AGGRESSIVE_TACTICS, MindTraits
    from show.guests.personas.vector import AGGRESSIVE_TACTICS as guest_tactics

    assert isinstance(traits, MindTraits)
    assert guest_tactics is AGGRESSIVE_TACTICS


if __name__ == "__main__":
    for fn in list(globals().values()):
        if callable(fn) and getattr(fn, "__name__", "").startswith("test_"):
            fn()
    print("OK: test_show_mind")
