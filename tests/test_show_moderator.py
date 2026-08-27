"""Unit tests for moderator routing helpers (allocate + post-update policy)."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.host.nodes import (
    decide_allocate_route,
    decide_moderator_route,
    make_route_after_allocate,
    make_route_after_update,
)
from show.host.persona import MODERATOR_PERSONA, ModeratorPersona


def test_moderator_persona_identity():
    assert MODERATOR_PERSONA.name == "Mr Bullshit"
    assert MODERATOR_PERSONA.agent_id == "moderator"
    assert "Scheduler" in MODERATOR_PERSONA.style
    assert MODERATOR_PERSONA.interject_threshold == 0.70
    assert MODERATOR_PERSONA.sentence_max == 2
    assert MODERATOR_PERSONA.signature == "On continue, restez avec nous !"


def test_decide_allocate_route():
    assert decide_allocate_route("guest_a", "guest_a") == "guest_a"
    assert decide_allocate_route("guest_b", "guest_a") == "guest_b"
    assert decide_allocate_route("other", "guest_a") == "guest_b"


def test_make_route_after_allocate_uses_current_speaker():
    guest_a = SimpleNamespace(agent_id="guest_a")
    route = make_route_after_allocate(guest_a)
    assert route({"current_speaker": "guest_a"}) == "guest_a"
    assert route({"current_speaker": "guest_b"}) == "guest_b"


def test_decide_moderator_route_mid_round_always_allocates():
    # Odd turn_index → round not complete → keep allocating, ignore tension/earpiece.
    assert (
        decide_moderator_route(
            turn_index=1,
            round_num=1,
            max_rounds=3,
            tension=0.99,
            interject_threshold=0.70,
            earpiece_pending=True,
        )
        == "moderator_allocate_floor"
    )


def test_decide_moderator_route_conclude_beats_earpiece_and_tension():
    assert (
        decide_moderator_route(
            turn_index=2,
            round_num=3,
            max_rounds=3,
            tension=0.99,
            interject_threshold=0.70,
            earpiece_pending=True,
        )
        == "moderator_conclude"
    )


def test_decide_moderator_route_earpiece_beats_tension_cadence():
    # Odd round + low tension would normally allocate; earpiece forces interject.
    assert (
        decide_moderator_route(
            turn_index=2,
            round_num=1,
            max_rounds=5,
            tension=0.1,
            interject_threshold=0.70,
            earpiece_pending=True,
        )
        == "moderator_interject"
    )


def test_decide_moderator_route_tension_above_threshold():
    assert (
        decide_moderator_route(
            turn_index=2,
            round_num=1,
            max_rounds=5,
            tension=0.71,
            interject_threshold=0.70,
            earpiece_pending=False,
        )
        == "moderator_interject"
    )


def test_decide_moderator_route_even_round_cadence():
    # Even round beat interjects even when tension is calm.
    assert (
        decide_moderator_route(
            turn_index=4,
            round_num=2,
            max_rounds=5,
            tension=0.1,
            interject_threshold=0.70,
            earpiece_pending=False,
        )
        == "moderator_interject"
    )


def test_decide_moderator_route_odd_round_calm_allocates():
    assert (
        decide_moderator_route(
            turn_index=2,
            round_num=1,
            max_rounds=5,
            tension=0.40,
            interject_threshold=0.70,
            earpiece_pending=False,
        )
        == "moderator_allocate_floor"
    )


def test_make_route_after_update_wires_peek_and_persona():
    peek = MagicMock(return_value=True)
    route = make_route_after_update(MODERATOR_PERSONA, peek_earpiece=peek)
    state = {
        "turn_index": 2,
        "round": 1,
        "max_rounds": 5,
        "tension": 0.0,
    }
    assert route(state) == "moderator_interject"
    peek.assert_called_once_with()

    peek.return_value = False
    custom = ModeratorPersona(
        name="Mr Bullshit",
        agent_id="moderator",
        style="test",
        signature="x",
        interject_threshold=0.50,
        sentence_max=2,
        temperature=0.8,
    )
    route_heat = make_route_after_update(custom, peek_earpiece=peek)
    assert route_heat({**state, "tension": 0.51}) == "moderator_interject"
    assert route_heat({**state, "tension": 0.49}) == "moderator_allocate_floor"


def test_make_route_after_update_without_peek():
    route = make_route_after_update(MODERATOR_PERSONA, peek_earpiece=None)
    state = {
        "turn_index": 2,
        "round": 1,
        "max_rounds": 5,
        "tension": 0.0,
    }
    assert route(state) == "moderator_allocate_floor"


if __name__ == "__main__":
    test_moderator_persona_identity()
    test_decide_allocate_route()
    test_make_route_after_allocate_uses_current_speaker()
    test_decide_moderator_route_mid_round_always_allocates()
    test_decide_moderator_route_conclude_beats_earpiece_and_tension()
    test_decide_moderator_route_earpiece_beats_tension_cadence()
    test_decide_moderator_route_tension_above_threshold()
    test_decide_moderator_route_even_round_cadence()
    test_decide_moderator_route_odd_round_calm_allocates()
    test_make_route_after_update_wires_peek_and_persona()
    test_make_route_after_update_without_peek()
    print("OK: test_show_moderator")
