"""Contrats backend : merge_minds, emit events, search None."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from show.memory.state import merge_minds
from show.runtime.events import EMIT_EVENT_TYPES, validate_emit_event
from show.runtime import llm as runtime_llm


def test_merge_minds_merges_deltas_without_clobber():
    left = {
        "guest_a": {
            "stance": 0.5,
            "conviction": 0.8,
            "valence": 0.0,
            "arousal": 0.2,
            "beliefs": [],
            "grudges": [],
            "inner_monologue": "",
        }
    }
    right = {
        "guest_b": {
            "stance": -0.5,
            "conviction": 0.7,
            "valence": 0.1,
            "arousal": 0.3,
            "beliefs": ["x"],
            "grudges": [],
            "inner_monologue": "y",
        }
    }
    merged = merge_minds(left, right)
    assert set(merged) == {"guest_a", "guest_b"}
    assert merged["guest_a"]["stance"] == 0.5
    assert merged["guest_b"]["beliefs"] == ["x"]


def test_merge_minds_right_overwrites_same_key():
    left = {"g": {"stance": 0.1, "conviction": 0.5, "valence": 0.0, "arousal": 0.1,
                  "beliefs": [], "grudges": [], "inner_monologue": ""}}
    right = {"g": {"stance": 0.9, "conviction": 0.5, "valence": 0.0, "arousal": 0.1,
                   "beliefs": [], "grudges": [], "inner_monologue": "new"}}
    assert merge_minds(left, right)["g"]["stance"] == 0.9
    assert merge_minds(None, right) == right
    assert merge_minds(left, None) == left


def test_validate_emit_event_accepts_known_types():
    for kind in EMIT_EVENT_TYPES:
        validate_emit_event({"type": kind})


def test_validate_emit_event_rejects_unknown():
    with pytest.raises(ValueError, match="unknown emit"):
        validate_emit_event({"type": "not_a_real_event"})


def test_search_returns_none_on_failure(monkeypatch):
    client = MagicMock()
    client.responses.create.side_effect = RuntimeError("network down")
    assert runtime_llm.search(client, "gpt-test", "query") is None


def test_search_returns_none_on_empty(monkeypatch):
    client = MagicMock()
    response = MagicMock()
    response.output_text = "   "
    client.responses.create.return_value = response
    assert runtime_llm.search(client, "gpt-test", "query") is None
