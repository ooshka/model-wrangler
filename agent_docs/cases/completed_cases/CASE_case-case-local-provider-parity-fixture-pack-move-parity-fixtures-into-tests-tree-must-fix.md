---
case_id: CASE_case-case-local-provider-parity-fixture-pack-move-parity-fixtures-into-tests-tree-must-fix
created: 2026-03-21
---

# CASE: Move Parity Fixtures Into Tests Tree Must Fix

## Slice metadata
- Type: hardening
- User Value: keeps executable fixture assets in the Python test surface instead of the agent-docs area, making project ownership and maintenance clearer for future contributors.
- Why Now: the new parity-fixture change introduced checked-in JSON files that are consumed by Python code, and review identified their current location under `agent_docs/testing/` as the wrong long-term boundary.
- Risk if Deferred: the repo will normalize storing runnable test fixtures in `agent_docs/`, blurring the distinction between planning/reference docs and project-owned test assets and making future tooling/layout decisions messier.

## Goal
Move the parity fixture JSON files into a test-owned project location and update the implementation, tests, and docs to follow that structure consistently.

## Why this next
- Value: restores a clean boundary between agent-facing planning docs and Python-native test assets.
- Dependency/Risk: closes the single merge-blocking workflow concern raised in review without widening into broader repo reorganization.
- Tech debt note: pays down layout debt immediately before more fixtures or E2E assets accumulate around the wrong directory pattern.

## Definition of Done
- [ ] The parity fixture JSON files live under a Python test-owned fixture directory rather than `agent_docs/testing/`.
- [ ] All code and tests that load those fixtures use the new location.
- [ ] Human-facing docs are updated to describe the new fixture-location pattern while keeping `agent_docs/testing/README.md` as the command/reference guide.
- [ ] Tests/verification: `python3 -m unittest tests.test_ollama_smoke tests.test_sqlite_exact_retrieval` and `python3 -m scripts.validate_local_provider_parity --db-path /tmp/local_llm_parity.sqlite3`

## Scope
**In**
- Relocating the parity fixture JSON files into the main Python project test surface.
- Updating the parity validation command, unit tests, and relevant docs to point at the new path.
- Clarifying the repo pattern that executable fixtures belong in the test tree while testing guidance remains in `agent_docs/testing/`.

**Out**
- Moving unrelated planning docs out of `agent_docs/`.
- Reorganizing older benchmark/reranker fixtures unless required for consistency with the new pattern.
- Changing parity command behavior beyond path updates needed for correctness.

## Proposed approach
Create a small fixture directory under the Python test surface, move the two parity JSON files there, and update the validator defaults plus any unit tests that refer to them. Keep the user-facing command unchanged if possible so the fix stays low-risk. Update both the repository README and `agent_docs/testing/README.md` to explain that executable test fixtures live with the test code while the agent docs remain the place for verification guidance and command selection.

## Steps (agent-executable)
1. Add a test-owned fixture directory and move the parity JSON files into it with minimal naming churn.
2. Update `scripts/validate_local_provider_parity.py` and any affected tests to resolve the fixtures from the new path.
3. Re-read the current docs and update the relevant references so they describe the new ownership pattern clearly.
4. Run the targeted unit tests and the parity validation command to confirm the relocation did not break behavior.

## Risks / Tech debt / Refactor signals
- Risk: path updates could silently break the parity command or docs examples. -> Mitigation: keep the command interface stable and re-run both the targeted tests and the documented command.
- Debt: pays down the newly introduced boundary confusion between `agent_docs/` and project-owned test assets.
- Refactor suggestion (if any): if more executable fixtures are added soon, consolidate them under one `tests/fixtures/` convention instead of scattering them across script-specific directories.

## Notes / Open questions
- Assumption: `tests/fixtures/` is the preferred destination because these files are consumed by Python tests and validation helpers.
- Assumption: older retrieval benchmark fixtures can remain where they are for now unless the implementation naturally benefits from moving them in the same narrow change.
