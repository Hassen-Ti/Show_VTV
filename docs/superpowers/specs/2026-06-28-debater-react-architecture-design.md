# Debater-Specific ReAct Architecture (ONPC Style)

**Date:** 2026-06-28  
**Status:** Approved — implemented 2026-06-28  
**Scope:** Agent 1 & Agent 2 debate turn pipeline (not moderator / fact-checker rewrite)

---

## 1. Problem

Current agents use LangChain `create_agent` — a generic ReAct loop (LLM ⇄ `search_web`). Persona lives in a single system prompt (`personas.py`, `get_system_prompt()`). There is no explicit debate cognition: no parse opponent → frame → tactic → character → TV delivery pipeline.

**Goal:** Replace generic ReAct with a **debater graph** modeled on French TV clash format (*On n'est pas couché*): short punchy replies, emotional spectacle, fact-backed attacks.

---

## 2. Architecture Overview

### 2.1 Hybrid graph (recommended)

Fixed cognitive pipeline + one tactical router mid-graph:

```
START → parse_opponent → choose_frame → [needs_evidence?] → search_web → select_tactic
      → draft_argument → apply_character → polish_onpc → END
```

### 2.2 Shared state (`DebateTurnState`)

| Field | Type | Set by |
|-------|------|--------|
| `topic` | str | Worker (input) |
| `opponent_last` | str | Worker — last opponent message or topic (round 1) |
| `debate_history` | str | Worker — formatted last 8 exchanges |
| `persona_vector` | dict | Agent class / persona config |
| `system_prompt_legacy` | str | Existing persona prompt (compat domains) |
| `parsed_claim` | str | `parse_opponent` |
| `weakness` | str | `parse_opponent` |
| `frame` | str | `choose_frame` |
| `needs_evidence` | bool | `choose_frame` |
| `evidence_query` | str | `choose_frame` |
| `evidence` | str \| None | `search_web` |
| `tactic` | str | `select_tactic` |
| `draft` | str | `draft_argument` |
| `final` | str | `polish_onpc` |
| `current_step` | str | Each node (for UI callbacks) |

### 2.3 Node responsibilities

| Node | ONPC role | LLM output constraint |
|------|-----------|----------------------|
| `parse_opponent` | "What did they say? Where's the flaw?" | JSON or structured lines: claim + weakness |
| `choose_frame` | Pick clash angle | frame + `needs_evidence` + optional query |
| `search_web` | One killer fact (tool, not LLM) | Reuse existing OpenAI `web_search_preview` |
| `select_tactic` | ONPC attack mode | One of: `clash`, `contradiction`, `pivot`, `moral_attack`, `expose_hypocrisy` |
| `draft_argument` | Journalist build — facts + logic | 3–5 sentences internal (not shown) |
| `apply_character` | Persona voice rewrite | Apply `persona_vector` knobs |
| `polish_onpc` | TV delivery | **Max 2 sentences**, punchline, French plateau |

Internal nodes use **low max_tokens** (80–150). Only `polish_onpc` output is streamed to the debate bubble.

---

## 3. Conditional edges

### 3.1 `choose_frame` → evidence branch

```python
def route_after_frame(state: DebateTurnState) -> str:
    if state["needs_evidence"] and state.get("evidence_query"):
        return "search_web"
    return "select_tactic"
```

**`needs_evidence = True` when:**
- Opponent cited a statistic, study, or "everyone knows" claim → debunk or counter-stat
- Agent's frame is fact-forward (`journalist` rhetoric mode)
- Round ≥ 2 and prior turn lacked sources (optional heuristic)

**`needs_evidence = False` when:**
- Pure moral / values clash
- Opponent argument is vague emotion → `moral_attack` or `pivot` without search
- Timeout / budget: skip search if `DEBATE_CONFIG["search_timeout_seconds"]` exceeded

### 3.2 `select_tactic` routing (ONPC distribution)

Tactic chosen by LLM with persona-biased prompt. Default weights:

| Persona side | Allowed tactics | Preferred |
|--------------|-----------------|-----------|
| Optimiste | clash, pivot_future, dismiss_fear | clash, pivot_future |
| Sceptique | contradiction, moral_attack, expose_hypocrisy | moral_attack, expose_hypocrisy |

Round 1 (no real opponent text): force `pivot` or `clash` on topic framing; skip `parse_opponent` weakness extraction or use topic-as-claim.

### 3.3 Error edges

- Any node LLM failure → fallback `draft_argument` with minimal prompt (topic + opponent_last) → `polish_onpc`
- `search_web` failure → `evidence = ""`, continue to `select_tactic` (debate without fact — ONPC allows passion-only ripostes)
- Empty `final` → return error string (existing worker behavior)

---

## 4. Character encoding (`persona_vector`)

Character is **not** a single adjective. Each agent maps to a constraint vector used in `apply_character` and `select_tactic`.

### 4.1 Schema

```python
PersonaVector = {
    "name": str,                    # display only
    "cognitive": str,             # accelerating | pragmatic | principled
    "affective": str,               # triumphant | indignant | sarcastic | cold
    "rhetoric": str,              # journalist | philosopher | lawyer | writer
    "tactics": list[str],           # allowed tactic ids
    "concession_rate": float,       # 0.0 ONPC default
    "sentence_max": int,            # 2 for ONPC
    "opener": str,                  # e.g. "Mais attendez —"
    "temperature_facts": float,     # parse, draft nodes
    "temperature_voice": float,     # apply_character, polish
    "forbidden": list[str],         # insults, slurs, ad hominem on person
}
```

### 4.2 Example vectors

**Agent 1 — optimiste ONPC**
```yaml
cognitive: accelerating
affective: triumphant
rhetoric: journalist
tactics: [clash, pivot_future, dismiss_fear]
concession_rate: 0.1
sentence_max: 2
opener: "Soyons sérieux :"
temperature_facts: 0.4
temperature_voice: 1.3
```

**Agent 2 — sceptique ONPC**
```yaml
cognitive: pragmatic
affective: indignant
rhetoric: journalist
tactics: [contradiction, moral_attack, expose_hypocrisy]
concession_rate: 0.0
sentence_max: 2
opener: "Mais attendez —"
temperature_facts: 0.3
temperature_voice: 1.2
```

### 4.3 Translation rules (prompt generation)

| Human trait | Prompt constraints |
|-------------|-------------------|
| Angry (ONPC) | Short sentences; moral indignation vocabulary; attack the **position** not the person; zero concession; opener interrupts opponent frame |
| Intelligent (ONPC) | One precise figure or named study; expose logical contradiction; no academic structure visible to audience |
| Sarcastic | Rhetorical questions; understated dismissal; never explain the joke |
| Triumphant | Future-oriented verbs; "regardez", "la réalité c'est"; dismiss fear as backward |

Legacy `personas.py` prompts remain as `system_prompt_legacy` injected into `draft_argument` for domain-specific vocabulary (économie, éducation, santé).

---

## 5. Streaming & UI integration

### 5.1 Current signals (unchanged contract)

- `messageStreamReceived(agent_key, chunk, round)` — public reply only
- `searchStarted(agent_key, searchInfo)` — left/right search label
- `messageCompleted`, `factCheckUpdate` — unchanged

### 5.2 New: step callback (optional spectacle)

Add optional `step_callback: Callable[[str], None]` to `run_react_turn()`:

| Step id | UI label (French) |
|---------|-------------------|
| `parse_opponent` | 🎯 Analyse de l'adversaire… |
| `choose_frame` | 🎬 Choix de l'angle d'attaque… |
| `search_web` | 🔍 Recherche d'un fait choc… |
| `select_tactic` | ⚔️ Préparation de la riposte… |
| `draft_argument` | ✍️ Construction de l'argument… |
| `apply_character` | 🎭 Mise en voix… |
| `polish_onpc` | 📺 Finalisation plateau… |

**Worker wiring:** `step_cb` → reuse `searchNotification` signal with formatted step text (no new QML signal in v1). Cleared on `messageComplete` (existing behavior).

**Public stream:** Only `polish_onpc` output word-streamed via existing `_simulate_stream` (or true token stream later).

### 5.3 Timing budget (ONPC)

Target **≤ 15s** per agent turn (existing `search_timeout_seconds`). Internal nodes: 6 LLM calls × ~1–2s each worst case → use `gpt-4o-mini` for internal nodes, `gpt-4o` for `polish_onpc` only (configurable in `DEBATE_GRAPH_CONFIG`).

---

## 6. Moderator & fact-checker integration

### 6.1 Moderator — no graph changes

Moderator stays outside the debater graph. Worker flow unchanged:

1. Moderator intro / give floor / interjection / conclusion
2. Agent turn via new graph
3. Fact-check on **final** public text only

`opponent_last` for Agent Two = Agent One's `final` from previous turn. `format_history_for_agent()` unchanged.

### 6.2 Fact-checker — consumes public output only

`AgentFactChecker.quick_fact_check(response, label)` runs on `polish_onpc` output. Internal `draft` may contain unverified claims — fact-checker validates what the audience sees.

Optional future: pass `evidence` source snippet to fact-checker for faster verification (out of scope v1).

### 6.3 Agent input message shape

Worker continues building:
```
{history_context}

{user_input}
```

Graph entry extracts `opponent_last` from user_input (last adversary message) and `debate_history` from history block.

---

## 7. File layout

```
src/agents/react/
  __init__.py              # export run_debate_turn
  executor.py              # thin wrapper: run_react_turn → run_debate_turn (compat)
  graph.py                 # StateGraph build + compile
  state.py                 # DebateTurnState TypedDict
  nodes/
    __init__.py
    parse.py
    frame.py
    tactic.py
    draft.py
    character.py
    polish.py
  tools/
    search.py              # move _execute_search_web here
  prompts/
    onpc_nodes.py          # micro-prompts per node

src/config/
  debate_graph.py          # DEBATE_GRAPH_CONFIG, persona vectors, tactic enums
  personas.py              # add persona_vector to each persona (or link by key)
```

`agent_1.py` / `agent_2.py`: add `get_persona_vector()`; keep `get_system_prompt()` for legacy text.

---

## 8. Configuration

```python
DEBATE_GRAPH_CONFIG = {
    "model_internal": "gpt-4o-mini",   # parse, frame, tactic, draft, character
    "model_delivery": "gpt-4o",        # polish_onpc
    "recursion_limit": 12,             # graph steps, not ReAct loops
    "enable_step_callbacks": True,
    "skip_search_round_1": False,      # ONPC: round 1 may still want opening stat
}
```

Persona vectors live in `debate_graph.py` with overrides per domain in `personas.py` (optional `vector_overrides` dict).

---

## 9. Testing strategy

| Test | What |
|------|------|
| `test_debate_graph_unit.py` | Each node with mocked LLM; assert state fields populated |
| `test_debate_graph_routing.py` | `needs_evidence` true/false routes correctly |
| `test_debate_graph_integration.py` | Full graph with real API (marked manual / env key) |
| `test_persona_vectors.py` | Agent 1/2 vectors match schema; tactics ⊆ allowed enum |
| Regression | `backend_bridge._run_agent_turn` still emits stream + fact-check |

Manual: run debate in UI — verify search labels show steps, replies stay 2 sentences, ONPC tone.

---

## 10. Migration & compatibility

- `BaseAgent.generate_react_debate_turn()` signature unchanged
- `run_react_turn()` delegates to `run_debate_turn()` in new module
- `enable_web_search=False` → skip `search_web` node always (direct path to tactic after frame)
- Domain personas: `system_prompt_legacy` merged into draft node; vectors can default by side (`optimiste` / `sceptique`)

---

## 11. Out of scope (v1)

- Rewriting moderator graph
- Visible internal reasoning in main text bubbles (only search label / step hints)
- Multi-agent asymmetric graphs (both agents share same graph structure, different vectors)
- True token streaming from OpenAI during polish (keep word simulation)

---

## 12. Success criteria

1. Agent replies feel like ONPC clash: short, emotional, fact-backed when needed
2. Internal pipeline is debuggable (state after each node loggable)
3. No breaking changes to QML bridge signals
4. Unit tests cover routing and persona schema
5. Latency per turn acceptable for live TV pacing (≤ 15s typical)
