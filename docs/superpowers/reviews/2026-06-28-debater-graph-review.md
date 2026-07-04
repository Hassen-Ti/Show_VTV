# Debater Graph Code Review — 2026-06-28

## Verdict

**APPROVED WITH NOTES** — ready for manual UI smoke test. Two issues found during review were fixed inline.

---

## Automated tests

| Test | Result |
|------|--------|
| `test_debate_graph_routing` | PASS |
| `test_debate_graph_unit` | PASS |
| `test_persona_vectors` | PASS |
| `test_debate_graph_compile` | PASS (added during review) |
| `test_debate_graph_integration` | PASS — 22.1s, 7 step callbacks, live API |

---

## Spec compliance (§12)

| # | Criterion | Status | Notes |
|---|-----------|--------|-------|
| 1 | ONPC tone, 2 sentences | **Manual** | Integration output ~2 sentences, clash tone OK |
| 2 | Debuggable pipeline | PASS | `current_step` per node; Mermaid at `examples/langgraph_debate_onpc.mmd` |
| 3 | QML signals | PASS | All four handlers present in `ModernDebateInterface.qml` |
| 4 | Unit tests | PASS | 4 test files green |
| 5 | Latency ≤ 15s | **NOTE** | Live turn measured **22.1s** (6–7 LLM calls on nano) |

---

## LangGraph compliance

| Check | Status |
|-------|--------|
| `StateGraph` + `context_schema=DebateGraphContext` | PASS |
| `invoke(state, context=...)` per turn | PASS |
| Partial state returns (no `{**state}`) | PASS — all 7 nodes |
| `add_conditional_edges` routing | PASS |
| No mutable `_runtime` singleton | PASS |

Reference: [LangGraph](https://github.com/langchain-ai/langgraph), [Graph API docs](https://docs.langchain.com/oss/python/langgraph/use-graph-api).

---

## Issues found & fixed during review

### 1. Empty-final error prefix (blocker — fixed)

- **Was:** `graph.py` returned `"Erreur: réponse vide..."` but worker only checks `"Error:"`.
- **Fix:** Unified to `"Error: réponse vide..."` in `src/agents/react/graph.py`.

### 2. Domain prompts ignored (gap — fixed)

- **Was:** `_run_agent_turn` always called `agent.get_system_prompt()`, ignoring `worker.prompt_one` / `prompt_two` set by `startDebate` (domain personas).
- **Fix:** `backend_bridge.py` now uses `self.prompt_one` / `self.prompt_two` per agent.

---

## Model & config (Task 4)

| Item | Value |
|------|-------|
| `OPENAI_MODEL` | `gpt-5.4-nano-2026-03-17` (`settings.py`) |
| Internal + delivery | Both use `OPENAI_MODEL` via `debate_graph.py` |
| `reasoning_effort` | `"none"` with `TypeError` fallback in `invoke_internal` |
| Hardcoded `gpt-4o` in `src/` | None found |

---

## Prompts (Task 5)

| Check | Status |
|-------|--------|
| `PERSONA_OPTIMISTE` / `SCEPTIQUE` schema valid | PASS |
| `gpt54_system.py` has `<output_contract>` per node | PASS |
| `draft` has `<grounding_rules>` | PASS |
| `polish` has `<verification_loop>` | PASS |
| `system_prompt_legacy` flows to `draft_argument` | PASS |

---

## Error handling (Task 6)

| Case | Status |
|------|--------|
| Search failure → empty evidence, continue | PASS |
| Empty `final` → `Error:` to worker | PASS (after fix) |
| `enable_web_search=False` → skip search | PASS + unit test |

---

## Out of scope (spec §11) — confirmed deferred

- Moderator not on LangGraph
- Step hints in search label only (not main bubbles)
- Word simulation streaming (not true OpenAI stream)
- Same graph for both agents (vectors differ)

---

## Follow-ups (non-blocking)

1. **Latency:** Consider merging internal nodes or caching frame/tactic to approach 15s budget.
2. **Test:** Add unit test for `skip_search_round_1=True` branch.
3. **Manual UI:** Run `uv run python main.py` — verify step labels + fact-check + stop debate.
4. **LangSmith:** Optional tracing per node for production debugging.

---

## Review execution

- Plan: `docs/superpowers/plans/2026-06-28-debater-graph-code-review.md`
- Method: Subagent-driven (explore subagent for Tasks 2/3/6 + inline fixes)
- Spec: `docs/superpowers/specs/2026-06-28-debater-react-architecture-design.md`
