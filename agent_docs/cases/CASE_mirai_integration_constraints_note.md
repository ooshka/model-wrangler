---
case_id: CASE_mirai_integration_constraints_note
created: 2026-03-15
---

# CASE: Mirai Integration Constraints Note

## Slice metadata
- Type: docs
- User Value: gives future `local_llm` provider work one explicit reference for the current `mirai` retrieval query contract and seam ownership, reducing the chance of local experiments drifting into the wrong public shape.
- Why Now: `mirai` just tightened its early-stage contract policy and moved query grounding fields under `metadata`, so the highest-value next step in `local_llm` is to capture those constraints before more local retrieval work resumes.
- Risk if Deferred: vector-index, reranker, or future adapter slices may continue targeting the older top-level query field shape or blur ownership between local provider artifacts and `mirai`'s MCP contract.

## Goal
Write one concise integration constraints note in `local_llm` that records the current `mirai` retrieval query metadata contract, clarifies what `local_llm` should and should not own, and points future local provider work at the right adapter boundary.

## Why this next
- Value: creates a small but explicit handoff artifact between the recently cleaned-up `mirai` query contract and the next local-provider slices.
- Dependency/Risk: lowers the risk that `local_llm` benchmarks or adapter prep work accidentally preserve stale top-level query fields or invent provider-owned envelope behavior.
- Tech debt note: pays down cross-repo contract ambiguity now, without widening into implementation or parity-fixture work.

## Definition of Done
- [ ] A docs note under `agent_docs/` records the current `mirai` retrieval query result shape relevant to `local_llm`, including `metadata.path`, `metadata.chunk_index`, and `metadata.snippet_offset`.
- [ ] The note clearly separates the local provider artifact `local_llm` should preserve from the MCP response envelope and policy/error behavior that remain owned by `mirai`.
- [ ] The note reflects `mirai`'s current early-stage contract posture: coordinated breaking refactors are allowed when they remove ambiguity and the consumer set is small.
- [ ] Existing `local_llm` retrieval contract docs are updated or cross-linked if needed so there is no contradictory guidance about top-level query fields.
- [ ] Tests/verification: re-read the new note against current `local_llm` docs and the latest `mirai` retrieval docs/roadmap language for consistency; no automated tests required for this docs-only slice.

## Scope
**In**
- Add one integration constraints note under `agent_docs/`.
- Capture the current observable `mirai` `/mcp/index/query` chunk shape that matters to local-provider planning.
- Clarify repo boundary ownership between local provider artifacts, adapter shaping, and `mirai` contract ownership.
- Update lightweight planning/docs references if needed for discoverability or to remove stale wording.

**Out**
- Any code changes in `local_llm` or `../mirai`.
- Vector index selection, reranker evaluation, or local retrieval implementation.
- New parity fixtures, benchmarks, or runtime wiring.

## Proposed approach
Use the existing `local_llm` retrieval artifact contract note plus the current `mirai` README/roadmap language as the source of truth for a narrow constraints document. Keep the note focused on the exact handoff boundary: `local_llm` should preserve ranked chunk artifacts and provider-facing semantics, while `mirai` owns MCP envelope shape, query contract refactors, and public error/policy behavior. Make the contract change posture explicit so future slices do not assume backward compatibility is required when only the known consumers are affected.

## Steps (agent-executable)
1. Inspect the current `local_llm` retrieval contract note and the latest `mirai` retrieval query docs to identify the exact contract points future local work must preserve.
2. Write a concise integration constraints note under `agent_docs/contracts/` or a similarly discoverable planning location, centered on the current `/mcp/index/query` chunk shape and boundary ownership.
3. Explicitly document that `mirai` now exposes grounding fields under `metadata`, and that `local_llm` should not treat old top-level `path`, `chunk_index`, or `snippet_offset` as the current target contract.
4. Record the early-stage contract posture: coordinated refactors are acceptable, and `local_llm` should be updated to match cleaner `mirai` contracts rather than freezing stale shapes.
5. Update any nearby contract/planning docs that would otherwise conflict with the new note, keeping the scope bounded to documentation consistency.

## Risks / Tech debt / Refactor signals
- Risk: the note could duplicate too much of the existing local retrieval contract and create two drifting sources of truth. -> Mitigation: frame this document as an integration constraints note and cross-reference the local provider artifact contract rather than restating all provider details.
- Risk: the note could overreach into implementation advice before the vector/index path is chosen. -> Mitigation: keep it at the contract and ownership boundary only.
- Debt: this slice still leaves concrete local adapter behavior and parity fixtures for later cases.
- Refactor signal: the existing local retrieval contract note currently shows the old top-level `mirai` chunk example, which is a direct drift signal this Case should correct or cross-link away.

## Notes / Open questions
- Assumption: the current `mirai` query metadata shape is stable enough for the next local-planning cycle even though early-stage contract refactors remain allowed.
- Assumption: this should stay docs-only because the immediate gap is cross-repo contract clarity, not missing local runtime capability.
