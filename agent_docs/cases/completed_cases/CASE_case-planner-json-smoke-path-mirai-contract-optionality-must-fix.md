---
case_id: CASE_case-planner-json-smoke-path-mirai-contract-optionality-must-fix
created: 2026-03-14
---

# CASE: Planner JSON Smoke Path Mirai Contract Optionality Must Fix

## Slice metadata
- Type: hardening
- User Value: keeps the local planner JSON smoke aligned with the actual `mirai` workflow planner seam so it does not reject outputs that the downstream consumer would accept.
- Why Now: the current review found the validator is stricter than `mirai` on optional fields, which undermines the purpose of the smoke path as a contract check.
- Risk if Deferred: local validation can produce false negatives, causing planner experiments to fail even when responses are compatible with `mirai`.

## Goal
Relax the local planner JSON validation to match the current `mirai` workflow planner normalization rules for optional `rationale`, optional `reason`, and optional-or-empty `params`.

## Why this next
- Value: restores the smoke path’s value as a reliable seam-alignment check rather than a stricter local policy.
- Dependency/Risk: blocks merge because the active Case explicitly claims alignment with the current `mirai` workflow planner shape.
- Tech debt note: pays down accidental contract drift introduced by local-only validation rules.

## Definition of Done
- [ ] Planner JSON validation accepts payloads that `mirai` currently normalizes successfully, including `nil`/missing optional rationale and missing `params` on an action.
- [ ] Unit tests cover the optionality cases that match the current `mirai` planner seam.
- [ ] Verification: `python3 -m unittest tests.test_ollama_smoke`

## Scope
**In**
- Adjust planner JSON validation in `scripts/ollama/smoke.py`.
- Update or extend unit tests in `tests/test_ollama_smoke.py`.

**Out**
- Prompt tuning changes.
- Any `mirai` code changes.
- Additional planner reliability heuristics beyond contract alignment.

## Proposed approach
Read the current `mirai` workflow planner normalization behavior and make the local validator match that narrow contract only. Preserve strict validation for malformed JSON and invalid types, but allow the optional fields and defaults that `mirai` already accepts. Keep the change local to the validator and its tests.

## Steps (agent-executable)
1. Confirm the current optional-field behavior in `mirai`'s workflow planner normalization path.
2. Update the local planner validator so `rationale` is optional and `params` defaults compatibly when absent.
3. Keep required-field checks for `actions` and per-action `action`.
4. Add unit tests for optional `rationale`, optional `reason`, and omitted `params`.
5. Run `python3 -m unittest tests.test_ollama_smoke`.

## Risks / Tech debt / Refactor signals
- Risk: loosening validation too far could let malformed responses through. -> Mitigation: only relax the fields that `mirai` already treats as optional.
- Debt: local contract checks now depend on mirrored knowledge of `mirai` behavior. -> Mitigation: keep tests explicit about which rules are borrowed from the current seam.
- Refactor suggestion (if any): if more local checks mirror `mirai`, consider capturing the contract in a lightweight fixture or note rather than duplicating behavior ad hoc.

## Notes / Open questions
- Assumption: `mirai` remains the source of truth for planner output normalization semantics.
