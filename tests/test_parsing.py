"""Parsing tactiques / labels LLM."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.parsing import first_allowed_tactic


def test_first_allowed_tactic_exact_label():
    allowed = ["clash", "moral_attack", "reframe"]
    assert first_allowed_tactic("TACTIC: moral_attack", allowed, "clash") == "moral_attack"


def test_first_allowed_tactic_ignores_substring_mentions():
    allowed = ["clash", "moral_attack", "reframe"]
    raw = "do not clash, prefer moral_attack\nTACTIC: moral_attack"
    assert first_allowed_tactic(raw, allowed, "clash") == "moral_attack"


def test_first_allowed_tactic_fallback_when_unknown():
    allowed = ["clash", "reframe"]
    assert first_allowed_tactic("TACTIC: pivot_future", allowed, "clash") == "clash"
