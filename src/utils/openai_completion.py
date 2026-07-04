"""Paramètres OpenAI Chat Completions selon le modèle (GPT-5 vs legacy)."""

from __future__ import annotations


def uses_max_completion_tokens(model: str) -> bool:
    """GPT-5.x n'accepte pas ``max_tokens`` — utiliser ``max_completion_tokens``."""
    name = (model or "").lower()
    return "gpt-5" in name or name.startswith("o1") or name.startswith("o3")


def chat_token_kwargs(model: str, limit: int) -> dict:
    if uses_max_completion_tokens(model):
        return {"max_completion_tokens": limit}
    return {"max_tokens": limit}
