"""Façade LLM du show — point de mock unique pour les tests."""

from __future__ import annotations

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import OpenAI

from config.show_config import SHOW_CONFIG
from utils.openai_completion import chat_token_kwargs


def think(
    model: str,
    system: str,
    user: str,
    *,
    temperature: float,
    max_tokens: Optional[int] = None,
) -> str:
    """Appel LLM interne (raisonnement, jamais diffusé tel quel)."""
    tokens = max_tokens or int(SHOW_CONFIG.get("internal_max_tokens", 160))
    effort = SHOW_CONFIG.get("reasoning_effort")
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


def search(client: OpenAI, model: str, query: str) -> Optional[str]:
    """Recherche web synthétisée pour un débat.

    Retourne le texte synthétisé, ou ``None`` si l'appel échoue / est vide.
    Les appelants doivent traiter ``None`` comme absence de preuve (pas de
    parsing de chaînes d'erreur localisées).
    """
    prompt = (
        "Synthétise des faits récents et vérifiables pour un débat télévisé. "
        "Sois concis (arguments factuels, pas d'intro). Question / angle :\n"
        f"{query}"
    )
    try:
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search_preview"}],
            input=prompt,
        )
        out = getattr(response, "output_text", None) or str(response)
        text = out.strip()[:8000]
        return text or None
    except Exception:
        return None
