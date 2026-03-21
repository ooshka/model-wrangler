---
case_id: CASE_retrieval_baseline_benchmark_upgrade_thresholds
created: 2026-03-21
---

# CASE: Retrieval Baseline Benchmark + Upgrade Thresholds

## Slice metadata
- Type: feature
- User Value: turns the SQLite exact retrieval baseline into measurable evidence so later ANN or `mirai` handoff work can rely on actual workstation behavior instead of assumptions.
- Why Now: the retrieval baseline implementation and benchmark helper now exist, and the next cross-project decision depends on proving whether exact search still fits the intended local workflow envelope.
- Risk if Deferred: `local_llm` may either over-rotate into premature ANN work or hand incomplete performance assumptions to `mirai`, increasing rework in both repos.

## Goal
Produce a small, repeatable benchmark slice that captures the SQLite exact retrieval baseline's build/query timing and explicit upgrade thresholds for this workstation class.

## Why this next
- Value: gives the repo a concrete evidence artifact for deciding whether exact search remains the right near-term retrieval path.
- Dependency/Risk: unblocks the later reranker and `mirai` provider-handoff slices by replacing vague performance assumptions with documented measurements.
- Tech debt note: pays down the current "ANN upgrade threshold is not measured yet" debt without widening into backend replacement or broad evaluation infrastructure.

## Approach Outline

### Utility (Why this helps now)
- Establishes one project-owned benchmark result shape that future retrieval planning can cite directly.
- Reduces the chance of reopening vector-backend selection based on intuition rather than measurements.

### Rationale (Why this approach)
- Prefer extending the existing benchmark helper and fixture path over introducing a separate benchmarking harness, because the repo already documents that command as the canonical baseline verification path.
- Keep the threshold output lightweight and repo-owned instead of adding machine-specific dashboards or large result archives; the decision needed now is "still acceptable or not," not long-term perf observability.

### Implementation Shape (How it will be done)
- Tighten `scripts/retrieval/sqlite_exact.py` so benchmark output includes the small evidence fields needed for planning, such as artifact size/corpus counts or similarly bounded context beyond raw timings.
- Add focused coverage in `tests/test_sqlite_exact_retrieval.py` for the new benchmark result shape and threshold-reporting behavior.
- Refresh the benchmark fixture and planning/testing docs under `agent_docs/testing/` and `agent_docs/plans/` so the canonical command, expected output, and upgrade triggers stay aligned.

### Risk & Validation Preview
- Risk: the benchmark result shape becomes too ad hoc to guide later slices. Validation: lock the output contract in targeted unit tests and keep fields bounded.
- Risk: threshold wording drifts away from what `mirai` actually needs for provider handoff. Validation: tie threshold criteria to current roadmap language about exact search versus ANN upgrade triggers.
- Risk: the slice turns into broad performance experimentation. Validation: keep one fixture, one documented command, and one concise threshold note as the Definition of Done.

## Definition of Done
- [ ] The benchmark command reports a stable, documented result shape that includes enough bounded context to evaluate the exact-search baseline on this workstation class.
- [ ] The repo documents explicit upgrade thresholds for revisiting ANN or service-backed retrieval, tied to the existing SQLite exact baseline rather than abstract future scale assumptions.
- [ ] Targeted unit tests cover any new benchmark output fields or threshold helpers added in this slice.
- [ ] `agent_docs/testing/README.md` and the relevant planning artifact point to the same canonical benchmark command and expected interpretation.
- [ ] Tests/verification: `python3 -m unittest tests.test_sqlite_exact_retrieval` and `python3 -m scripts.retrieval.sqlite_exact --db-path /tmp/local_llm_retrieval.sqlite3 --fixture agent_docs/testing/sqlite_exact_benchmark_fixture.json`

## Scope
**In**
- Extend the existing SQLite benchmark path enough to produce planning-grade measurements.
- Document explicit upgrade thresholds for when exact search should be reconsidered.
- Keep the benchmark artifact, fixture, and docs aligned with the current local retrieval contract.

**Out**
- Adding Faiss, HNSW, Qdrant, or another ANN/vector backend.
- Running large corpus experiments across multiple machines.
- Changing `mirai` contracts or wiring.
- Reranker evaluation beyond preserving a clean follow-on seam.

## Proposed approach
Build on the current benchmark command instead of inventing a second evaluation path. Keep the implementation centered on `scripts/retrieval/sqlite_exact.py`, where the repo already measures build and query time from a fixture-backed SQLite artifact. Add only the minimum extra result context needed to interpret those timings, then document the explicit upgrade thresholds in planning/testing docs so later decisions stay anchored to one reproducible command. The main code touch points should stay narrow: benchmark result assembly, its focused unit tests, and the docs that define how to run and read the benchmark.

## Steps (agent-executable)
1. Inspect the current benchmark helper, fixture, and testing/docs references to identify the minimum missing evidence fields and where upgrade-threshold wording should live.
2. Extend the benchmark path in `scripts/retrieval/sqlite_exact.py` with any bounded result fields or helper logic needed to make the command planning-usable without widening into a new harness.
3. Add or update targeted tests in `tests/test_sqlite_exact_retrieval.py` to lock the benchmark output shape and any threshold-related helper behavior.
4. Update `agent_docs/testing/README.md` and the relevant planning doc so the benchmark command, expected result interpretation, and ANN upgrade triggers all match.
5. Run the targeted unit test and benchmark command, then capture any follow-on reranker or `mirai` handoff implications in backlog/planning notes only if they emerge directly from this slice.

## Risks / Tech debt / Refactor signals
- Risk: adding too many benchmark fields could turn a simple helper into an unstable mini-reporting tool. -> Mitigation: restrict output to the smallest set of metrics/context needed for upgrade decisions.
- Debt: this slice still leaves broader corpus-shape evaluation and multi-fixture comparison for later if the first benchmark shows ambiguity.
- Refactor suggestion (if any): if benchmark formatting or threshold evaluation grows beyond a few helper functions, extract a small result-builder/helper module instead of expanding `sqlite_exact.py` inline indefinitely.

## Notes / Open questions
- Assumption: one representative fixture and one canonical command are sufficient for the current planning decision.
- Assumption: upgrade thresholds should be qualitative but concrete enough to drive the next planner handoff, not tuned as hard SLOs yet.
