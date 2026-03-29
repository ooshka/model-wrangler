---
case_id: CASE_local_workflow_failure_fixture_pack
created: 2026-03-29
---

# CASE: Local Workflow Failure Fixture Pack

## Slice metadata
- Type: feature
- User Value: gives `mirai` implementors runnable local evidence for planner and drafter failure categories before they extend the self-hosted workflow execute path.
- Why Now: `mirai` has already landed the canonical workflow execute endpoint, so the next self-hosted workflow slice should consume bounded local failure expectations instead of guessing at provider/runtime ownership.
- Risk if Deferred: `mirai` will either stall on self-hosted workflow follow-ons or bake in incorrect failure mapping assumptions that later need contract cleanup.

## Goal
Add one small executable fixture-based check that proves the expected local planner and draft failure categories and documents how to run it.

## Why this next
- Value: turns the current draft and planner smoke helpers into reusable workflow failure evidence that another repo can consume directly.
- Dependency/Risk: unblocks the next `mirai` local workflow execution mapping slice while keeping retrieval work separate.
- Tech debt note: pays down the current gap where failure ownership is implied by one-off smoke output instead of encoded in project-owned fixtures.

## Definition of Done
- [ ] A project-owned fixture or tightly related fixture pair covers planner and draft failure expectations for the local workflow seam.
- [ ] The existing smoke/parity helper code can execute the new failure fixture path and return a compact pass summary.
- [ ] `tests.test_ollama_smoke` covers the new failure fixture runner and key mismatch cases.
- [ ] `agent_docs/testing/README.md` documents the narrow verification command and expected output for the new workflow failure check.
- [ ] Tests/verification: `python3 -m unittest tests.test_ollama_smoke`

## Scope
**In**
- Extend the current fixture-driven workflow validation path for planner and draft failure categories.
- Add or update JSON fixture data under `tests/fixtures/` for bounded workflow failure expectations.
- Update smoke helper/tests/docs only as needed to expose one clear verification command.

**Out**
- Live runtime reliability expansion beyond the fixture-driven failure checks.
- Retrieval artifact validation or retrieval benchmark changes.
- Any `mirai` code or MCP error-envelope assertions.

## Proposed approach
Build on the existing planner parity-fixture pattern in `scripts/ollama/smoke.py` instead of creating a new standalone harness. Add a workflow failure fixture that exercises both planner and draft classification helpers against representative local-provider failure messages, then expose one small runner summary and cover it with focused unit tests in `tests/test_ollama_smoke.py`. Keep the fixture contract local-provider scoped: category, boundary, and owner only. Update `agent_docs/testing/README.md` so implementors have one obvious verification command before handing evidence back to `mirai`.

## Steps (agent-executable)
1. Inspect the existing planner parity fixture flow in `scripts/ollama/smoke.py` and the current fixture files in `tests/fixtures/` to identify the smallest extension point for workflow failure checks.
2. Add project-owned fixture data for planner and draft failure expectations, covering at least runtime-unavailable, malformed payload, and invalid diff shape where applicable.
3. Extend the smoke helper with one bounded runner that validates the new workflow failure fixture data and returns a compact JSON summary without asserting any `mirai` API envelopes.
4. Add or update `tests/test_ollama_smoke.py` to cover the happy path and at least one mismatch failure for the new fixture runner.
5. Update `agent_docs/testing/README.md` with the narrow verification command and the expected success/failure interpretation for the workflow failure fixture check.

## Risks / Tech debt / Refactor signals
- Risk: the fixture runner could overfit to current error-message strings and become brittle. → Mitigation: keep expectations scoped to the existing local classification boundaries already tested in helper units.
- Risk: scope could creep into broader parity or runtime-retry work. → Mitigation: keep this Case fixture-only and explicitly defer live runtime reliability expansion.
- Debt: pays down the missing reusable workflow failure evidence called out in planning notes, but still leaves retrieval contract exercising as a separate follow-on.
- Refactor suggestion (if any): if planner and draft fixture flows start duplicating validation scaffolding, extract a small shared helper only after this Case lands and only if it reduces test fragility.

## Notes / Open questions
- Assume the best shape is one workflow-focused fixture runner, not separate top-level commands for planner and drafter, unless the existing helper structure makes that materially more complex.
- Assume success output should stay comparison-oriented and compact, similar to the current parity fixture summaries.
