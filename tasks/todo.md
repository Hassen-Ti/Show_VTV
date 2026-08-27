# Backend track — self-validated

## Boundary

**IN:** `src/show/{guests,host,memory,runtime,graph,parsing}` + config/utils  
**OUT:** QML, `backend_bridge`, `main.py`  
**API:** `run_show` + emit + earpiece on `ShowContext`

## Done

- [x] Merge #4 → #3 → #6 → #2 (skip #5 UI)
- [x] B1 `merge_minds` + guest deltas
- [x] B3 `decide_after_update` + `has_earpiece(context)` only
- [x] B5 `runtime/events.py` typed emit + smoke validation
- [x] B12 `search` → `Optional[str]` / `None` on failure
- [x] pytest green

## Deferred (next)

- Memory ↔ PersonaVector decoupling (B2)
- LLM client reuse on context (B11)
- Dead-node registration cleanup (B7)
- UI PR #5 after startDebate earpiece race fix

## Review

Branch `eng/backend-contracts`. Contracts hardened without new frameworks.
