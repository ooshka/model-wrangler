---
case_id: CASE_local_workflow_draft_patch_smoke_path
created: 2026-03-21
---

# CASE: Local Workflow Draft Patch Smoke Path

## Slice metadata
- Type: feature
- User Value: gives `local_llm` a repeatable local draft-patch proof path so `mirai` can wire the next self-hosted workflow seam without guessing at patch shape or failure behavior.
- Why Now: `mirai` has finished the local planner-provider handoff and intentionally kept workflow draft generation on the hosted path, so the next cross-project blocker is missing local draft-patch runtime evidence in `local_llm`.
- Risk if Deferred: `mirai`'s next patch-drafter handoff slice would have to infer local draft request/response behavior from planner assumptions instead of a repo-owned smoke path and bounded failure expectations.

## Goal
Add one small local draft-patch smoke path in `local_llm` that proves a bounded OpenAI-compatible draft response shape and reports deterministic failure categories for the self-hosted workflow seam.

## Why this next
- Value: unlocks the next concrete `mirai` provider handoff by turning patch-drafting from a narrative assumption into executable local evidence.
- Dependency/Risk: directly unblocks `mirai`'s `Local Workflow Patch Drafter Provider Handoff Case` while keeping the local planner and local patch seams distinct.
- Tech debt note: pays down the current gap where planning is smoke-tested locally but draft generation is not, without widening into full patch-quality evaluation.

## Definition of Done
- [ ] `scripts/ollama/smoke.py` exposes one bounded workflow-draft smoke mode that exercises the OpenAI-compatible local chat/completions path and validates a canonical single-file unified-diff draft response.
- [ ] The smoke helper reports deterministic failure categories for at least runtime-unavailable, malformed-draft-payload, and invalid-diff-shape cases owned by `local_llm`.
- [ ] Focused unit coverage exists for the draft smoke parser/validator and failure categorization path.
- [ ] `README.md` and `agent_docs/testing/README.md` document the canonical draft smoke command and how it differs from planner smoke/parity checks.
- [ ] Tests/verification: `python3 -m unittest tests.test_ollama_smoke` and `python3 scripts/ollama/smoke.py --draft-patch-only`

## Scope
**In**
- A narrow draft-patch-specific smoke mode in the existing Ollama smoke helper.
- Bounded diff-shape validation for a canonical `workflow.draft_patch`-style response payload or extracted patch string.
- Targeted tests and docs updates for the new smoke command and local failure categories.

**Out**
- Full patch quality scoring or semantic correctness evaluation.
- `mirai` API envelope assertions or endpoint wiring changes.
- Local retrieval contract exerciser work.

## Proposed approach
Reuse the existing `scripts/ollama/smoke.py` owner for local runtime HTTP plumbing instead of creating a second patch-specific script. Add a draft smoke mode that sends one small deterministic drafting request against the OpenAI-compatible chat completions path, extracts a proposed patch payload, and validates only the stable structural boundary `mirai` will care about: one non-empty unified diff targeting one markdown path. Keep failure reporting bounded to local-provider/runtime evidence. Mirror the planner smoke pattern in the unit tests and docs so the repo ends with one clear command for planner smoke, one for draft smoke, and the existing parity fixture helper for offline checks.

## Steps (agent-executable)
1. Inspect the existing planner smoke and patch-related contract notes to identify the smallest reusable parser/validator seam for local draft output.
2. Add a draft-patch-only smoke mode to `scripts/ollama/smoke.py` that calls the local OpenAI-compatible endpoint with one bounded drafting prompt and validates the returned unified diff shape.
3. Add deterministic failure categorization for runtime, malformed payload, and invalid diff-shape outcomes without asserting `mirai` error envelopes.
4. Extend `tests/test_ollama_smoke.py` with focused coverage for draft parsing, validation, and failure-category handling.
5. Update `README.md` and `agent_docs/testing/README.md` with the canonical draft smoke command, prerequisites, and interpretation guidance.

## Risks / Tech debt / Refactor signals
- Risk: draft smoke could overfit model wording instead of the patch boundary `mirai` actually needs. -> Mitigation: validate only the minimal unified-diff structure and target-path shape, not exact patch content.
- Risk: planner and drafter smoke logic could fork into duplicated request plumbing. -> Mitigation: extend the existing smoke helper with shared request/parse utilities rather than adding a parallel script.
- Debt: this slice still leaves patch-quality scoring and broader draft reliability coverage for later once `mirai` has a concrete local drafter seam.
- Refactor suggestion (if any): if planner and draft smoke modes grow more complex, extract a small shared response-validation module under `scripts/ollama/` instead of widening one file indefinitely.

## Notes / Open questions
- Assumption: the first local draft smoke should target a response that contains or cleanly extracts a unified diff string, not a richer provider-specific metadata envelope.
- Assumption: validating a single-file markdown patch boundary is enough to unblock the next `mirai` drafter-provider handoff slice.
