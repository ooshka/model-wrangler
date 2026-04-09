---
case_id: CASE_local_workflow_edit_intent_smoke_path
created: 2026-04-08
---

# CASE: Local Workflow Edit Intent Smoke Path

## Slice metadata
- Type: feature
- User Value: gives `local_llm` a repeatable local proof path for the new `mirai` workflow drafter contract so self-hosted draft work can proceed without relying on unified-diff text generation.
- Why Now: `mirai` has now merged the `edit_intent` contract and expects both hosted and local workflow draft providers to normalize to the same JSON shape, making local contract evidence the next concrete cross-repo unblocker.
- Risk if Deferred: `mirai`'s local drafter handoff will either stall on provider uncertainty or regress into one-off prompt experiments instead of project-owned runtime evidence.

## Goal
Add one small local smoke path that proves the workflow model can return strict `edit_intent` JSON aligned with `mirai`'s current single-file `replace_content` contract.

## Why this next
- Value: turns the `edit_intent` pivot from a planning note into executable provider evidence that `mirai` can consume directly.
- Dependency/Risk: directly unblocks the next local-provider handoff in `mirai` while keeping execute/apply bridging and broader reliability work out of scope.
- Tech debt note: pays down the current mismatch where repo docs still describe unified-diff draft smoke even though the contract owner has moved to `edit_intent`.

## Definition of Done
- [ ] `scripts/ollama/smoke.py` exposes one bounded workflow draft smoke mode that validates a local OpenAI-compatible response against `mirai`'s current `edit_intent` shape: `{ "edit_intent": { "path": "...", "operation": "replace_content", "content": "..." } }`.
- [ ] The smoke helper reports deterministic local failure categories for at least runtime-unavailable, malformed-draft-payload, and invalid-edit-intent-shape outcomes without asserting `mirai` MCP envelopes.
- [ ] Focused unit coverage exists for edit-intent parsing, validation, and failure categorization in the existing smoke test module.
- [ ] `README.md` and `agent_docs/testing/README.md` document the canonical edit-intent smoke command and remove or clearly supersede the prior draft-patch smoke wording.
- [ ] Tests/verification: `python3 -m unittest tests.test_ollama_smoke` and `python3 scripts/ollama/smoke.py --edit-intent-only`

## Scope
**In**
- A narrow edit-intent-specific smoke mode in the existing Ollama smoke helper.
- Validation for the current `mirai` v1 draft contract: single markdown path, `replace_content`, and string note content.
- Targeted tests and docs updates for the new command and bounded local failure interpretation.

**Out**
- Direct `mirai` code changes or MCP endpoint assertions.
- Broader workflow reliability sampling across multiple prompts or larger contexts.
- Execute/apply bridging, patch synthesis, or retrieval contract work.

## Proposed approach
Extend the existing `scripts/ollama/smoke.py` workflow draft seam instead of adding a second script. Replace the current draft-patch request/validation path with a small prompt that asks for only the `edit_intent` JSON contract `mirai` now expects, then validate only the stable server-owned boundary: matching markdown path, supported `replace_content` operation, and string content normalized enough for note replacement. Keep failure reporting local-provider scoped so the resulting smoke output stays useful to `mirai` implementors without pretending to be an MCP contract test. Mirror that change through the existing unit-test and documentation surfaces so there is one obvious local command for workflow draft evidence.

## Steps (agent-executable)
1. Confirm the current `mirai` workflow drafter contract shape and the smallest local smoke surface that still exercises the OpenAI-compatible chat/completions path.
2. Update `scripts/ollama/smoke.py` to add or rename the workflow draft smoke mode around `edit_intent` JSON generation and validation for the bounded single-file `replace_content` case.
3. Add deterministic failure categorization for malformed JSON/edit-intent payloads and invalid contract-shape outcomes while preserving the existing runtime-unavailable handling pattern.
4. Extend `tests/test_ollama_smoke.py` with focused coverage for edit-intent parsing, validation, and failure summaries.
5. Update `README.md` and `agent_docs/testing/README.md` so the repo's documented workflow smoke path matches the new contract and verification command.

## Risks / Tech debt / Refactor signals
- Risk: the local prompt could still overfit output phrasing instead of the contract boundary. → Mitigation: validate only the `edit_intent` object shape and semantic constraints that `mirai` currently enforces.
- Risk: docs and smoke flags could drift if the old draft-patch naming lingers beside the new flow. → Mitigation: make the edit-intent command canonical and remove or clearly replace stale wording in the same slice.
- Debt: pays down the obsolete unified-diff smoke assumption, but broader multi-prompt reliability evidence remains a separate follow-on once this bounded seam is proven.
- Refactor suggestion (if any): if planner and workflow-draft response validators keep converging on shared JSON-shape helpers, consider a small local validation module under `scripts/ollama/` in a later slice instead of growing one file indefinitely.

## Notes / Open questions
- Assumption: the first local workflow edit-intent proof should stay at `replace_content` only, matching the current `mirai` contract.
- Assumption: the smoke output should remain comparison-oriented and compact, similar to the current planner and failure-fixture summaries.
