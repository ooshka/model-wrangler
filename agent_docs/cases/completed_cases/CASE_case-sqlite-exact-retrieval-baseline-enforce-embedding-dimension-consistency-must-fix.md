---
case_id: CASE_case-sqlite-exact-retrieval-baseline-enforce-embedding-dimension-consistency-must-fix
created: 2026-03-21
---

# CASE: Enforce Embedding Dimension Consistency Must Fix

## Slice metadata
- Type: hardening
- User Value: keeps the SQLite retrieval artifact queryable after repeated indexing runs by preventing mixed-dimension embeddings from corrupting the local index.
- Why Now: the new retrieval baseline persists embeddings but does not enforce one embedding dimensionality across the artifact, so one mismatched row can crash every future query.
- Risk if Deferred: a single bad insert, fixture mistake, or embedding-model change can leave the persisted SQLite artifact in a state where retrieval fails with a dimension mismatch at query time.

## Goal
Ensure the SQLite exact retrieval artifact either rejects mixed embedding dimensions on write or cleanly isolates them so query-time ranking cannot crash on persisted dimension mismatches.

## Why this next
- Value: protects the core retrieval path from a persistent corruption mode.
- Dependency/Risk: blocks merge because the current query path can raise on stored mixed-dimension data after the artifact has already been written.
- Tech debt note: pays down a schema-contract gap before more retrieval or benchmark code depends on the artifact format.

## Definition of Done
- [ ] Writes enforce a consistent embedding dimensionality for one SQLite artifact, or queries explicitly constrain themselves to compatible stored rows.
- [ ] Query-time ranking no longer crashes when the artifact contains or is offered mismatched embedding dimensions.
- [ ] Focused tests cover the mixed-dimension failure path and the chosen mitigation.
- [ ] Tests/verification: `python3 -m unittest tests.test_sqlite_exact_retrieval`

## Scope
**In**
- `scripts/retrieval/sqlite_exact.py`
- `tests/test_sqlite_exact_retrieval.py`

**Out**
- Benchmark-threshold policy changes.
- ANN or vector-service work.
- Any `mirai` adapter changes.

## Proposed approach
Treat embedding dimensionality as part of the retrieval artifact contract, not a best-effort convention. The smallest safe fix is to validate artifact dimensions on write and/or query so the index never reaches a persistent state where one row causes a runtime crash. Keep the behavior explicit and covered by tests.

## Steps (agent-executable)
1. Decide whether the artifact should enforce one stored dimension globally or filter/query by dimension safely.
2. Update the SQLite retrieval code so mixed dimensions are rejected or isolated before cosine ranking runs.
3. Add a regression test that reproduces the current mixed-dimension failure and proves the new behavior.
4. Re-run the retrieval unit tests.

## Risks / Tech debt / Refactor signals
- Risk: an incomplete fix could silently skip rows without making the artifact contract clear. → Mitigation: make the behavior explicit in code and tests.
- Debt: this closes a contract hole in the first artifact format.
- Refactor suggestion (if any): if artifact metadata grows, consider a small artifact-manifest table instead of scattering invariants across row-level columns.

## Notes / Open questions
- Assumption: one SQLite artifact should correspond to one embedding model/dimension set.
