"""Tests paramètres token OpenAI selon modèle."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.openai_completion import chat_token_kwargs, uses_max_completion_tokens


def test_gpt5_uses_max_completion_tokens():
    assert uses_max_completion_tokens("gpt-5.4-nano-2026-03-17")
    kw = chat_token_kwargs("gpt-5.4-nano-2026-03-17", 150)
    assert kw == {"max_completion_tokens": 150}
    assert "max_tokens" not in kw


def test_gpt4o_uses_max_tokens():
    assert not uses_max_completion_tokens("gpt-4o")
    kw = chat_token_kwargs("gpt-4o", 150)
    assert kw == {"max_tokens": 150}


if __name__ == "__main__":
    test_gpt5_uses_max_completion_tokens()
    test_gpt4o_uses_max_tokens()
    print("OK: test_openai_completion")
