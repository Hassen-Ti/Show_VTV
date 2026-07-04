"""Utilitaires partagés pour les nœuds du graphe débatteur."""

from __future__ import annotations

import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.runtime import Runtime

from agents.react.context import DebateGraphContext
from config.debate_graph import DEBATE_GRAPH_CONFIG, STEP_LABELS
from utils.openai_completion import chat_token_kwargs


def notify_step(runtime: Runtime[DebateGraphContext], step_id: str) -> None:
    if not DEBATE_GRAPH_CONFIG.get("enable_step_callbacks", True):
        return
    callback = runtime.context.step_callback
    if callback:
        callback(STEP_LABELS.get(step_id, step_id))


def invoke_internal(
    model: str,
    system: str,
    user: str,
    *,
    temperature: float,
    max_tokens: Optional[int] = None,
) -> str:
    tokens = max_tokens or int(DEBATE_GRAPH_CONFIG.get("internal_max_tokens", 120))
    effort = DEBATE_GRAPH_CONFIG.get("reasoning_effort")
    llm_kwargs: dict = {
        "model": model,
        "temperature": temperature,
        **chat_token_kwargs(model, tokens),
    }
    if effort:
        llm_kwargs["reasoning_effort"] = effort
    try:
        llm = ChatOpenAI(**llm_kwargs)
    except TypeError:
        llm_kwargs.pop("reasoning_effort", None)
        llm = ChatOpenAI(**llm_kwargs)
    msg = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
    )
    return (msg.content or "").strip()


def parse_labeled_lines(text: str, labels: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for label in labels:
        match = re.search(rf"^{label}:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
        if match:
            result[label.lower()] = match.group(1).strip()
    return result


def parse_yes_no(value: str) -> bool:
    normalized = (value or "").strip().lower()
    return normalized in {"oui", "yes", "true", "1", "vrai"}


def first_allowed_tactic(raw: str, allowed: list[str], fallback: str) -> str:
    normalized = (raw or "").strip().lower()
    for tactic in allowed:
        if tactic in normalized:
            return tactic
    return fallback
