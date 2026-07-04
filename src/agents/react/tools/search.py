"""Recherche web pour le graphe débatteur."""

from __future__ import annotations

from openai import OpenAI


def execute_search_web(client: OpenAI, model: str, query: str) -> str:
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
        return out.strip()[:8000]
    except Exception as e:
        return f"Erreur lors de la recherche web: {e}"
