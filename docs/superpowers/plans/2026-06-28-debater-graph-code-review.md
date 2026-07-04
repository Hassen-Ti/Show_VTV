# Debater Graph Code Review Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the ONPC debater LangGraph implementation is correct, spec-compliant, and safe to ship before manual UI testing.

**Architecture:** Review against `docs/superpowers/specs/2026-06-28-debater-react-architecture-design.md`, LangGraph idioms (`StateGraph` + `context_schema` + partial state updates), and existing PyQt bridge contracts.

**Tech Stack:** LangGraph 1.1.x, LangChain OpenAI, OpenAI Responses API (`web_search_preview`), PyQt6/QML bridge, `gpt-5.4-nano-2026-03-17`

**Spec reference:** `docs/superpowers/specs/2026-06-28-debater-react-architecture-design.md`

---

## File map (what to review)

| File | Responsibility |
|------|----------------|
| `src/agents/react/graph.py` | `StateGraph` build, compile, `invoke(state, context=)` |
| `src/agents/react/context.py` | `DebateGraphContext` runtime deps |
| `src/agents/react/state.py` | `DebateTurnState`, `initial_state`, input extraction |
| `src/agents/react/routing.py` | `route_after_frame` conditional edge |
| `src/agents/react/nodes/*.py` | 7 nodes — each returns partial state |
| `src/agents/react/prompts/gpt54_system.py` | GPT-5.4 nano system contracts |
| `src/agents/react/prompts/onpc_nodes.py` | User prompts per node |
| `src/agents/react/executor.py` | Public `run_react_turn` wrapper |
| `src/config/debate_graph.py` | Model, persona vectors, tactics |
| `src/config/settings.py` | `OPENAI_MODEL` single source of truth |
| `src/agents/agent_1.py` / `agent_2.py` | `get_persona_vector()` |
| `src/agents/base_agent.py` | `generate_react_debate_turn` + `step_callback` |
| `src/backend_bridge.py` | `step_cb` → `searchNotification` |
| `tests/test_debate_graph_*.py` | Unit tests |
| `examples/langgraph_debate_onpc_graph.py` | Mermaid export smoke |

---

## Review checklist (spec §12 success criteria)

| # | Criterion | How to verify |
|---|-----------|---------------|
| 1 | ONPC clash tone, 2 sentences | Manual UI + inspect `polish_onpc` prompt limits |
| 2 | Debuggable pipeline | Log `current_step` after invoke; Mermaid export |
| 3 | No QML signal breakage | Grep bridge signals; manual debate |
| 4 | Unit tests pass | Run all `test_debate_graph_*` + `test_persona_vectors` |
| 5 | Latency ≤ 15s typical | Time one full turn with API key (optional) |

---

### Task 1: Automated tests — baseline green

**Files:**
- Test: `tests/test_debate_graph_routing.py`
- Test: `tests/test_debate_graph_unit.py`
- Test: `tests/test_persona_vectors.py`

- [ ] **Step 1: Run all debate unit tests**

```bash
cd "c:\Users\tilio\Desktop\Projets Dev AI\CURSOR_PROJECT\Show_VTV"
uv run python tests/test_debate_graph_routing.py
uv run python tests/test_debate_graph_unit.py
uv run python tests/test_persona_vectors.py
```

Expected: each prints `OK: ...` and exit code 0.

- [ ] **Step 2: Compile LangGraph and export Mermaid**

```bash
uv run python examples/langgraph_debate_onpc_graph.py
```

Expected: writes `examples/langgraph_debate_onpc.mmd` with nodes:
`parse_opponent → choose_frame → (search_web?) → select_tactic → draft_argument → apply_character → polish_onpc`.

- [ ] **Step 3: Record pass/fail in review notes**

If any step fails, stop and fix before Task 2.

---

### Task 2: LangGraph pattern compliance

**Files:**
- Read: `src/agents/react/graph.py`
- Read: `src/agents/react/context.py`
- Read: `src/agents/react/nodes/parse.py` (sample node)

- [ ] **Step 1: Verify `context_schema` pattern**

Confirm in `graph.py`:

```python
graph = StateGraph(DebateTurnState, context_schema=DebateGraphContext)
# ...
compiled.invoke(state, context=context, config={"recursion_limit": ...})
```

**Pass if:** No mutable `_runtime` on a singleton runner; context passed per invoke.

- [ ] **Step 2: Verify partial state returns**

Open each node in `src/agents/react/nodes/`. Each `return` must be a **partial dict** (only changed keys), not `{**state, ...}`.

Example pass (`parse.py`):

```python
return {
    "parsed_claim": opponent,
    "weakness": "...",
    "current_step": "parse_opponent",
}
```

**Fail if:** any node spreads full state unnecessarily (not a blocker but non-idiomatic).

- [ ] **Step 3: Verify conditional routing**

In `src/agents/react/routing.py`, confirm three branches match spec §3.1:

1. `enable_web_search=False` → `select_tactic`
2. `skip_search_round_1` + round 1 → `select_tactic`
3. `needs_evidence` + non-empty `evidence_query` → `search_web`
4. else → `select_tactic`

Cross-check `graph.py` maps: `{"search_web": "search_web", "select_tactic": "select_tactic"}`.

---

### Task 3: Bridge & API contract (no QML breakage)

**Files:**
- Read: `src/backend_bridge.py` (`_run_agent_turn`)
- Read: `src/agents/base_agent.py` (`generate_react_debate_turn`)
- Read: `src/ui/qml/ModernDebateInterface.qml` (signal handlers)

- [ ] **Step 1: Confirm public agent API unchanged**

`BaseAgent.generate_react_debate_turn(user_input, system_prompt, stream_callback, search_callback, step_callback)` must still exist and return `str`.

- [ ] **Step 2: Confirm worker wiring**

In `backend_bridge.py`, `_run_agent_turn` must pass:

```python
response = agent.generate_react_debate_turn(
    user_message,
    system_prompt,
    stream_callback=stream_cb,
    search_callback=search_cb,
    step_callback=step_cb,
)
```

And `step_cb` must emit `searchNotification` (reused for step labels per spec §5.2).

- [ ] **Step 3: Confirm QML still listens**

Grep `ModernDebateInterface.qml` for:
- `onMessageStreamReceived`
- `onSearchStarted` (step labels land here)
- `onMessageCompleted` (clears search label)
- `onFactCheckUpdate`

**Pass if:** all four handlers exist and unchanged in signature.

---

### Task 4: Model & config consistency

**Files:**
- Read: `src/config/settings.py`
- Read: `src/config/debate_graph.py`
- Read: `src/agents/agent_1.py`, `agent_2.py`, `agent_moderator.py`, `agent_factchecker.py`

- [ ] **Step 1: Single model source**

```bash
rg "gpt-4o|OPENAI_MODEL|gpt-5" src/config src/agents --glob "*.py"
```

Expected:
- `OPENAI_MODEL = "gpt-5.4-nano-2026-03-17"` in `settings.py`
- Agents use `OPENAI_MODEL` (not hardcoded `gpt-4o`)
- `DEBATE_GRAPH_CONFIG["model_internal"]` and `["model_delivery"]` both reference `OPENAI_MODEL`

- [ ] **Step 2: Reasoning effort**

In `debate_graph.py`, confirm `reasoning_effort: "none"` for nano narrow tasks.

In `nodes/common.py`, confirm `invoke_internal` tries `reasoning_effort` with `TypeError` fallback.

---

### Task 5: Persona vectors & prompts

**Files:**
- Read: `src/config/debate_graph.py` (`PERSONA_OPTIMISTE`, `PERSONA_SCEPTIQUE`)
- Read: `src/agents/react/prompts/gpt54_system.py`
- Read: `src/agents/react/prompts/onpc_nodes.py`

- [ ] **Step 1: Persona schema**

Run:

```bash
uv run python tests/test_persona_vectors.py
```

Manually verify optimiste vs sceptique differ on:
- `affective`: `triumphant` vs `indignant`
- `tactics`: disjoint allowed sets
- `sentence_max`: 2

- [ ] **Step 2: GPT-5.4 nano contracts**

Each node system prompt in `gpt54_system.py` must include `<output_contract>`.

Structured nodes (`parse`, `frame`, `tactic`) must use closed labels (`CLAIM:`, `FRAME:`, `TACTIC:`).

`draft` must include `<grounding_rules>` (no invented stats).

`polish` must include `<verification_loop>` and length limit.

- [ ] **Step 3: Legacy persona injection**

Confirm `draft_argument` receives `state["system_prompt_legacy"]` from `initial_state` (domain personas from `personas.py` flow through `system_prompt` param).

**Known gap to flag (not blocking v1):** `backend_bridge._run_agent_turn` calls `agent.get_system_prompt()` and ignores `worker.prompt_one/prompt_two` — domain override may not apply unless agents are updated separately. Note in review if still true.

---

### Task 6: Error handling & edge cases

**Files:**
- Read: `src/agents/react/nodes/search.py`
- Read: `src/agents/react/tools/search.py`
- Read: `src/agents/react/graph.py` (`run_debate_turn`)

- [ ] **Step 1: Search failure is non-fatal**

`search_web` node: if `execute_search_web` returns `"Erreur..."`, evidence becomes `""` and graph continues to `select_tactic`.

- [ ] **Step 2: Empty final handling**

`run_debate_turn` returns `"Erreur: réponse vide..."` if `final` empty; worker treats `Error:` prefix as failure (`backend_bridge.py`).

- [ ] **Step 3: `enable_web_search=False` path**

When disabled, `route_after_frame` must always return `select_tactic` (never `search_web`).

Add quick test if missing:

```python
# tests/test_debate_graph_routing.py — already has test_route_skips_search_when_disabled
```

---

### Task 7: Add missing unit test — graph compiles with Runtime

**Files:**
- Create: `tests/test_debate_graph_compile.py`

- [ ] **Step 1: Write compile smoke test**

```python
"""Smoke: graphe LangGraph compile et structure des nœuds."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.react.graph import build_debate_graph, draw_debate_graph_mermaid


def test_graph_compiles():
    compiled = build_debate_graph()
    assert compiled is not None


def test_mermaid_contains_all_nodes():
    mermaid = draw_debate_graph_mermaid()
    for node in (
        "parse_opponent",
        "choose_frame",
        "search_web",
        "select_tactic",
        "draft_argument",
        "apply_character",
        "polish_onpc",
    ):
        assert node in mermaid


if __name__ == "__main__":
    test_graph_compiles()
    test_mermaid_contains_all_nodes()
    print("OK: test_debate_graph_compile")
```

- [ ] **Step 2: Run test**

```bash
uv run python tests/test_debate_graph_compile.py
```

Expected: `OK: test_debate_graph_compile`

---

### Task 8: Optional integration test (requires `OPENAI_API_KEY`)

**Files:**
- Create: `tests/test_debate_graph_integration.py`

Skip if no API key — manual only.

- [ ] **Step 1: Write integration test (guarded)**

```python
"""Integration manuelle — nécessite OPENAI_API_KEY."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def test_one_debate_turn_live():
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: no OPENAI_API_KEY")
        return
    from openai import OpenAI
    from config.debate_graph import get_persona_vector
    from agents.react.graph import run_debate_turn

    client = OpenAI()
    steps: list[str] = []

    result = run_debate_turn(
        client=client,
        model="gpt-5.4-nano-2026-03-17",
        temperature=1.1,
        max_tokens=150,
        system_prompt="Tu es un débatteur optimiste TV.",
        user_input="L'IA va-t-elle détruire l'emploi en 2025?",
        persona_vector=get_persona_vector("optimiste"),
        enable_web_search=True,
        step_callback=steps.append,
    )
    assert result and not result.startswith("Error:")
    assert len(result) > 20
    print("FINAL:", result[:200])
    print("STEPS:", len(steps))


if __name__ == "__main__":
    test_one_debate_turn_live()
    print("OK: integration (or SKIP)")
```

- [ ] **Step 2: Run (optional)**

```bash
uv run python tests/test_debate_graph_integration.py
```

Expected: prints `FINAL:` + `OK`, or `SKIP` without API key.

**Review latency:** note wall-clock time; flag if > 30s per turn (6+ LLM calls on nano).

---

### Task 9: Manual UI smoke test

**Files:**
- Run: `main.py`
- Watch: `ModernDebateInterface.qml` behavior

- [ ] **Step 1: Launch app**

```bash
uv run python main.py
```

- [ ] **Step 2: Start debate (default topic, moderator on)**

Observe:
1. Step labels appear in search area (🎯, 🎬, 🔍, ⚔️, 🎭, 📺)
2. Agent bubbles stream word-by-word
3. Fact-checker updates after each agent message
4. Replies are ~2 sentences, French, confrontational

- [ ] **Step 3: Stop debate mid-run**

Confirm no crash; `debateStatusChanged(false)` fires.

---

### Task 10: Review verdict document

**Files:**
- Create: `docs/superpowers/reviews/2026-06-28-debater-graph-review.md`

- [ ] **Step 1: Fill review template**

```markdown
# Debater Graph Code Review — 2026-06-28

## Verdict
- [ ] APPROVED — ready for use
- [ ] APPROVED WITH NOTES — minor follow-ups
- [ ] CHANGES REQUIRED — blockers listed below

## Automated tests
| Test | Result |
|------|--------|
| test_debate_graph_routing | |
| test_debate_graph_unit | |
| test_persona_vectors | |
| test_debate_graph_compile | |
| test_debate_graph_integration | SKIP / PASS |

## Spec compliance (§12)
1. ONPC tone: 
2. Debuggable: 
3. QML signals: 
4. Unit tests: 
5. Latency: 

## LangGraph compliance
- context_schema: 
- partial state: 
- conditional edges: 

## Blockers (if any)
- 

## Follow-ups (non-blocking)
- Domain personas via worker.prompt_one/two
- True token streaming for polish
- LangSmith tracing for node latency
```

- [ ] **Step 2: List known acceptable gaps (spec §11 out of scope)**

Confirm these are intentionally deferred, not bugs:
- Moderator not on LangGraph
- Step hints only in search label, not main bubbles
- Word simulation streaming (not true OpenAI stream)
- Same graph structure for both agents (vectors differ only)

---

## Self-review (plan vs spec)

| Spec section | Covered by task |
|--------------|-----------------|
| §2 Architecture (7 nodes) | Task 2, 7 |
| §3 Conditional edges | Task 2, 6 |
| §4 Persona vectors | Task 5 |
| §5 Streaming/UI | Task 3, 9 |
| §6 Moderator/fact-check | Task 3 (unchanged) |
| §8 Config/models | Task 4 |
| §9 Testing | Task 1, 7, 8 |
| §10 Migration | Task 3 |
| §12 Success criteria | Task 10 checklist |

**Gaps intentionally not in this review plan:**
- Performance profiling under load (out of scope)
- Commit/PR creation (user must request)

---

## Execution order (recommended)

1. Task 1 → Task 7 (automated, fast)
2. Task 2 → Task 6 (static code review)
3. Task 4 → Task 5 (config/prompts)
4. Task 8 (optional, needs API key)
5. Task 9 (manual UI)
6. Task 10 (write verdict)

**Estimated time:** 45–90 minutes (15 min without live API/UI).
