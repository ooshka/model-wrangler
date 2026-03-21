---
case_id: CASE_local_provider_parity_fixture_pack
created: 2026-03-21
---

# CASE: Local Provider Parity Fixture Pack

## Slice metadata
- Type: hardening
- User Value: gives future `mirai` provider work reusable local retrieval and planner evidence instead of relying on one-off smoke outputs or implicit assumptions.
- Why Now: retrieval baseline, benchmark thresholds, reranker evaluation, and planner JSON smoke are already in place, so the next highest-value step is to turn those point checks into explicit parity and failure-behavior fixtures before deeper planner-provider wiring resumes in `mirai`.
- Risk if Deferred: `mirai`'s next local planner/provider slice will guess at local failure semantics and expected output shape, increasing drift risk between repos and making later regression checks ad hoc.

## Goal
Add one small fixture pack plus validation helpers that make local retrieval and planner parity expectations explicit, repeatable, and easy to reuse in later `mirai` handoff work.

## Why this next
- Value: creates durable evidence for the current local-provider contract instead of requiring each follow-on slice to rediscover expected retrieval and planner behavior.
- Dependency/Risk: directly unblocks the next `mirai` planner-provider feature slice by clarifying which local behaviors are already proven, which failures are expected, and which outputs should be treated as parity targets.
- Tech debt note: pays down stale "single smoke is enough" planning debt without widening into production provider wiring or large fixture infrastructure.

## Definition of Done
- [ ] The repo contains one small fixture pack under `agent_docs/testing/` that covers both retrieval-artifact parity expectations and planner JSON parity expectations relevant to `mirai` integration.
- [ ] There is a narrow validation helper or command surface that can run those fixtures without requiring a human to manually inspect free-form smoke output.
- [ ] Failure expectations are documented for at least runtime-unavailable and malformed-planner-payload scenarios, with clear separation between provider-side evidence and `mirai`-owned API behavior.
- [ ] Focused unit tests cover fixture validation behavior without changing the existing default retrieval benchmark or planner smoke commands.
- [ ] `agent_docs/testing/README.md` documents the canonical parity-fixture verification command(s) and when they should be run before `mirai` provider-handoff work.
- [ ] Tests/verification: `python3 -m unittest tests.test_ollama_smoke tests.test_sqlite_exact_retrieval` and one documented parity-fixture command.

## Scope
**In**
- A bounded retrieval/planner fixture pack owned by `local_llm`.
- A small validation seam around the existing retrieval and planner smoke/evaluation helpers.
- Documentation that states which parity expectations belong to local-provider evidence versus `mirai` API ownership.

**Out**
- Wiring a local planner provider into `mirai`.
- Expanding the fixture pack into a broad benchmark matrix or prompt bakeoff.
- Changing the existing retrieval artifact contract or `mirai` MCP contract.

## Proposed approach
Keep the slice centered on existing repo-owned seams instead of adding new subsystems. Reuse the current retrieval and planner smoke helpers as the execution path, but introduce a small fixture layer that records expected retrieval result shape, planner action shape, and a few key failure cases. The implementation should stay local to `agent_docs/testing/`, `scripts/ollama/smoke.py`, and the current unit-test surfaces so the follow-on `mirai` provider-handoff Case can rely on a concrete artifact pack rather than narrative docs alone.

## Steps (agent-executable)
1. Inspect the current retrieval benchmark/rerank fixtures and planner smoke helpers to identify the smallest common validation seam for fixture-driven parity checks.
2. Add one or more project-owned fixture files under `agent_docs/testing/` that encode retrieval expected-shape checks and planner JSON expected-shape/failure checks.
3. Extend the relevant helper script or adjacent validator with a comparison-oriented mode that evaluates fixture expectations without changing existing default smoke behavior.
4. Add focused unit tests for fixture parsing, deterministic comparison output, and the documented failure-path summaries.
5. Update `agent_docs/testing/README.md` with the canonical parity-fixture command(s), prerequisites, and interpretation guidance.
6. Record any remaining follow-on gap for the `mirai` planner-provider handoff in planning docs without widening this Case into adapter implementation.

## Risks / Tech debt / Refactor signals
- Risk: the fixture pack could blur provider-side evidence with `mirai` API ownership. -> Mitigation: keep retrieval artifact expectations separate from `mirai` envelope semantics and document the boundary explicitly.
- Risk: planner parity checks could become flaky if they rely on unconstrained model wording. -> Mitigation: validate only bounded structural expectations and declared failure summaries, not exact natural-language phrasing.
- Risk: this slice could turn into a broad evaluation framework. -> Mitigation: keep it to one small reusable fixture pack and one validation seam layered on top of existing helpers.
- Debt: pays down the current reliance on one-off smoke outputs before the next cross-repo handoff.
- Refactor suggestion (if any): if retrieval and planner fixture validation start sharing too much comparison logic, extract a tiny `tests` or `scripts` helper rather than expanding the smoke script inline.

## Notes / Open questions
- Assumption: parity evidence should focus on structural expectations and failure categories, not exact provider score parity or prompt-text parity.
- Assumption: one small fixture pack is enough to unblock the next `mirai` handoff; broader scenario coverage can remain a later hardening follow-on if real drift appears.
