"""Cache ChatOpenAI : une instance par clé de config."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from show.runtime import llm as runtime_llm


def test_think_reuses_chat_openai_for_same_params(monkeypatch):
    runtime_llm.clear_chat_model_cache()
    instances = []

    class FakeChat:
        def __init__(self, **kwargs):
            instances.append(kwargs)
            self.kwargs = kwargs

        def invoke(self, messages):
            msg = MagicMock()
            msg.content = "ok"
            return msg

    monkeypatch.setattr(runtime_llm, "ChatOpenAI", FakeChat)
    monkeypatch.setattr(
        runtime_llm,
        "chat_token_kwargs",
        lambda model, tokens: {"max_tokens": tokens},
    )
    monkeypatch.delitem(runtime_llm.SHOW_CONFIG, "reasoning_effort", raising=False)

    a = runtime_llm.think("m", "sys", "user", temperature=0.5, max_tokens=100)
    b = runtime_llm.think("m", "sys", "user2", temperature=0.5, max_tokens=100)
    assert a == "ok" and b == "ok"
    assert len(instances) == 1

    runtime_llm.think("m", "sys", "user3", temperature=0.9, max_tokens=100)
    assert len(instances) == 2


def test_clear_chat_model_cache():
    runtime_llm._chat_models[("x", 0.1, 10, "")] = MagicMock()
    runtime_llm.clear_chat_model_cache()
    assert runtime_llm._chat_models == {}
