---
case_id: CASE_case-sqlite-exact-retrieval-baseline-reset-benchmark-state-must-fix
created: 2026-03-21
---

# CASE: Reset Benchmark State Must Fix

## Slice metadata
- Type: hardening
- User Value: keeps the documented benchmark helper trustworthy by ensuring repeated runs measure the intended fixture instead of stale rows from earlier executions.
- Why Now: the README and testing guide now present the benchmark helper as the way to capture baseline build/query timings, but the helper reuses any existing SQLite file and accumulates old rows.
- Risk if Deferred: repeated benchmark runs can report misleading chunk counts, query timings, and top-result context because prior data remains in the artifact.

## Goal
Make the retrieval benchmark helper run against a known artifact state so benchmark output reflects only the current fixture input.

## Why this next
- Value: restores the benchmark command as a reliable planning input instead of a stateful demo.
- Dependency/Risk: blocks merge because the current documented benchmark path can produce misleading numbers without warning.
- Tech debt note: pays down a reproducibility gap in the new retrieval workflow before it becomes part of future upgrade-threshold decisions.

## Definition of Done
- [ ] The benchmark helper starts from a known SQLite artifact state or clearly uses an isolated benchmark database path by default.
- [ ] Repeated benchmark runs with the same fixture produce stable chunk counts that reflect only the fixture rows.
- [ ] Focused tests cover the stale-artifact regression or the new reset/isolation behavior.
- [ ] Tests/verification: `python3 -m unittest tests.test_sqlite_exact_retrieval` and `python3 -m scripts.retrieval.sqlite_exact --db-path /tmp/local_llm_retrieval.sqlite3 --fixture agent_docs/testing/sqlite_exact_benchmark_fixture.json`

## Scope
**In**
- `scripts/retrieval/sqlite_exact.py`
- `tests/test_sqlite_exact_retrieval.py`
- `README.md` and/or `agent_docs/testing/README.md` if command semantics change

**Out**
- Retrieval ranking algorithm changes unrelated to benchmark isolation.
- ANN follow-up work.
- `mirai` integration.

## Proposed approach
Benchmark commands should be reproducible by default. The smallest safe fix is to make the helper reset or isolate the benchmark artifact before loading the fixture, then add a regression test so repeated runs cannot silently accumulate state again. Keep the user-facing command clear in the docs if semantics change.

## Steps (agent-executable)
1. Update the benchmark helper so it does not silently reuse stale rows from prior runs.
2. Add a regression test that executes repeated benchmark/setup flows and asserts stable chunk counts.
3. Adjust docs only if the benchmark command or expectations change.
4. Re-run the targeted tests and benchmark command.

## Risks / Tech debt / Refactor signals
- Risk: a partial fix could still leave hidden state in the benchmark path. → Mitigation: cover repeated-run behavior in tests, not just one clean run.
- Debt: this removes hidden state from a measurement path the planning docs now depend on.
- Refactor suggestion (if any): if more evaluation commands appear, consider a shared helper for disposable artifact setup instead of duplicating reset logic.

## Notes / Open questions
- Assumption: benchmark reproducibility matters more than preserving prior benchmark artifacts at the documented default path.
