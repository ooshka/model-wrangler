---
case_id: CASE_case-case-retrieval-baseline-benchmark-upgrade-thresholds-benchmark-note-count-artifact-scope-must-fix
created: 2026-03-21
---

# CASE: Benchmark Note Count Must Reflect Artifact Scope

## Slice metadata
- Type: hardening
- User Value: keeps benchmark output trustworthy when contributors reuse an existing SQLite artifact, so upgrade-threshold decisions are based on the actual measured corpus rather than only the latest fixture input.
- Why Now: the benchmark case added `note_count` as planning evidence, but the current implementation reports only the unique note paths in the current input chunk batch.
- Risk if Deferred: repeated benchmark runs with `--no-reset` can under-report corpus scope and make ANN upgrade decisions look safer than they are.

## Goal
Make benchmark corpus-count reporting reflect the resulting SQLite artifact state instead of only the current fixture payload.

## Why this next
- Value: restores consistency between `chunk_count`, `artifact_bytes`, and note-scope reporting in the benchmark output.
- Dependency/Risk: blocks merge because the current benchmark JSON can mislead the very upgrade-threshold workflow this Case introduced.
- Tech debt note: pays down a result-shape inconsistency before later reranker or `mirai` handoff work starts relying on benchmark output.

## Definition of Done
- [ ] Benchmark output reports note scope from the resulting retrieval artifact, including `--no-reset` runs that accumulate previously stored chunks.
- [ ] Targeted tests cover both reset and no-reset benchmark flows with note-count assertions aligned to artifact state rather than fixture scope.
- [ ] README/testing docs describe the corrected note-count semantics consistently with the command output.
- [ ] Tests/verification: `python3 -m unittest tests.test_sqlite_exact_retrieval` and `python3 -m scripts.retrieval.sqlite_exact --db-path /tmp/local_llm_retrieval.sqlite3 --fixture agent_docs/testing/sqlite_exact_benchmark_fixture.json --no-reset`

## Scope
**In**
- Benchmark note-count/result-shape logic in `scripts/retrieval/sqlite_exact.py`.
- Focused tests in `tests/test_sqlite_exact_retrieval.py`.
- Any directly affected benchmark docs in `README.md` and `agent_docs/testing/README.md`.

**Out**
- New benchmark metrics unrelated to corpus-scope correctness.
- Threshold tuning beyond what is required to describe the corrected metric semantics.
- Reranker or ANN implementation work.

## Proposed approach
Keep the fix narrow: derive note count from the persisted artifact after the benchmark write, not from the current input chunk list. That keeps the new field aligned with `chunk_count` and `artifact_bytes`, which already describe the resulting SQLite state. Update the existing benchmark tests to cover both reset and reused-artifact flows, then adjust docs only where they currently imply the wrong scope.

## Steps (agent-executable)
1. Inspect the current benchmark result assembly and identify the smallest way to compute unique note count from the resulting SQLite artifact.
2. Update benchmark logic so `note_count` reflects artifact state after the write/reset behavior has completed.
3. Adjust targeted tests to lock the corrected note-count behavior for both reset and `--no-reset` paths.
4. Update benchmark docs only where they currently describe fixture-scoped note counts.
5. Re-run the targeted unit test and the benchmark command with `--no-reset` to confirm the corrected semantics.

## Risks / Tech debt / Refactor signals
- Risk: a partial fix could make note counting depend on fixture shape in one path and artifact state in another. -> Mitigation: cover both reset and no-reset flows explicitly in tests.
- Debt: benchmark output still remains a lightweight planning aid, not a full observability surface.
- Refactor suggestion (if any): if benchmark result metadata keeps growing, consider a small helper for result assembly so metric semantics stay centralized.

## Notes / Open questions
- Assumption: artifact-scope note counting is the intended contract because the benchmark is documenting upgrade-threshold context for the resulting retrieval state.
