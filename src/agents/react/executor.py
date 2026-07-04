"""

Tour de débat ONPC via LangGraph : pipeline débatteur (parse → frame → tactic → delivery).

"""



from __future__ import annotations



from typing import TYPE_CHECKING, Callable, Optional



from agents.react.graph import run_debate_turn

from config.debate_graph import get_persona_vector



if TYPE_CHECKING:

    from openai import OpenAI





def _simulate_stream(text: str, stream_callback: Optional[Callable[[str], None]]) -> None:

    if not stream_callback or not text:

        return

    for word in text.split():

        stream_callback(word + " ")





def run_react_turn(

    client: OpenAI,

    model: str,

    temperature: float,

    max_tokens: int,

    system_prompt: str,

    user_input: str,

    enable_web_search: bool,

    stream_callback: Optional[Callable[[str], None]] = None,

    search_callback: Optional[Callable[[str], None]] = None,

    step_callback: Optional[Callable[[str], None]] = None,

    persona_vector: Optional[dict] = None,

    max_steps: Optional[int] = None,

    topic: str = "",

) -> str:

    """Un tour de débat : graphe débatteur ONPC (remplace create_agent générique)."""

    _ = max_steps

    vector = persona_vector or get_persona_vector("optimiste")

    return run_debate_turn(

        client=client,

        model=model,

        temperature=temperature,

        max_tokens=max_tokens,

        system_prompt=system_prompt,

        user_input=user_input,

        persona_vector=vector,

        enable_web_search=enable_web_search,

        stream_callback=stream_callback,

        search_callback=search_callback,

        step_callback=step_callback,

        topic=topic,

    )


