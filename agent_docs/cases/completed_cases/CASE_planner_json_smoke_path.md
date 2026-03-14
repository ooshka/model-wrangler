---
case_id: CASE_planner_json_smoke_path
created: 2026-03-14
---

# CASE: Planner JSON Smoke Path

## Slice metadata
- Type: feature
- User Value: proves the local planner model can return the strict JSON object shape that `mirai` workflow orchestration expects before any provider handoff work starts.
- Why Now: the Ollama baseline is in place, but it only validates freeform chat output; the next meaningful interface risk is whether the local planner path can produce parseable structured plans reliably enough for seam experimentation.
- Risk if Deferred: retrieval and planner follow-ons could expand around an unvalidated assumption, increasing the chance that later `mirai` wiring stalls on malformed local planner responses.

## Goal
Add a narrow, repeatable local planner JSON smoke workflow in `local_llm` that exercises the Ollama OpenAI-compatible chat endpoint with a strict JSON response contract and validates the returned structure against the current `mirai` workflow planner shape.

## Why this next
- Value: upgrades the current baseline from "model responds" to "model responds in the structured shape the next consumer will need".
- Dependency/Risk: directly reduces the highest near-term contract risk called out in the tech debt log without widening into `mirai` integration or retrieval infrastructure.
- Tech debt note: keeps contract validation local and lightweight, avoiding premature provider abstraction while preventing more planner experiments from depending on prompt-only assumptions.

## Definition of Done
- [ ] The repo has a project-owned planner JSON smoke path alongside the existing Ollama smoke flow.
- [ ] The planner smoke uses an explicit expected JSON object contract aligned with `mirai`'s current workflow planner output shape: top-level `rationale` plus `actions`, with each action containing `action`, optional `reason`, and object `params`.
- [ ] The smoke path fails clearly when the local model response is non-JSON, missing required keys, or uses invalid field types.
- [ ] Automated tests cover the local JSON validation/helpers for the new smoke path.
- [ ] `README.md` and `agent_docs/testing/README.md` document how to run the planner JSON smoke command and what success/failure looks like.

## Scope
**In**
- Extend the current Ollama smoke tooling or add a sibling helper for planner-specific structured-output validation.
- Define one small, stable planner prompt/input payload that expects the workflow planner JSON object shape.
- Validate returned JSON locally and surface actionable failure messages.
- Update docs and testing guidance for the new command.

**Out**
- Any changes to `../mirai`.
- Broader planner prompt tuning or benchmark work.
- Provider abstraction for non-Ollama runtimes.
- Retrieval/index/reranker implementation.

## Proposed approach
Build on the existing `scripts/ollama/smoke.py` path so the repo keeps one small owner for local Ollama request plumbing. Add a planner-specific mode that requests JSON-only output from the local chat completion endpoint, parses the returned message content, and validates the resulting object against the narrowest useful subset of `mirai`'s workflow planner contract. Keep the first slice focused on deterministic smoke coverage and failure reporting rather than scoring reliability across many prompts.

## Steps (agent-executable)
1. Inspect the current smoke script and identify the minimal extension point for a planner JSON mode without duplicating HTTP/config helpers.
2. Add a planner JSON request path that sends an explicit JSON-only instruction and a bounded sample planning intent/context payload.
3. Parse the returned message content as JSON and validate the required object shape and field types expected by the `mirai` workflow planner seam.
4. Surface clear error messages for malformed JSON, missing keys, empty actions, or invalid action payload types.
5. Add unit tests for the JSON parsing/validation helpers and any new CLI mode behavior that can be exercised without a live runtime.
6. Update `README.md` and `agent_docs/testing/README.md` with the new planner JSON smoke command, expected successful output, and likely failure modes.
7. Record any follow-on reliability concerns in planning artifacts without expanding this Case into prompt tuning or parity-fixture work.

## Risks / Tech debt / Refactor signals
- Risk: the local model may occasionally wrap JSON in prose or code fences even with explicit instructions. -> Mitigation: fail closed in this slice and log follow-on hardening separately instead of adding permissive cleanup heuristics immediately.
- Risk: `mirai`'s planner contract could evolve slightly before provider handoff. -> Mitigation: validate only the stable core shape already enforced in the current workflow planner normalization path.
- Debt: the smoke script will own both freeform and structured planner checks, which can become crowded if more evaluation modes are added.
- Refactor signal: if a second structured-output workflow appears, extract request/validation helpers into a small local module rather than growing one script indefinitely.

## Notes / Open questions
- Assumption: the local validation target is the current `mirai` workflow planner core shape, not a future provider-specific extension.
- Assumption: one bounded sample intent/context pair is sufficient for the first local JSON contract smoke.
