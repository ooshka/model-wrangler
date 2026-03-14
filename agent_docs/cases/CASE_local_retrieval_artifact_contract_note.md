---
case_id: CASE_local_retrieval_artifact_contract_note
created: 2026-03-14
---

# CASE: Local Retrieval Artifact Contract Note

## Slice metadata
- Type: docs
- User Value: defines the local retrieval artifact shape clearly enough that the first `mirai` adapter slice can target a stable local contract instead of reverse-engineering ad hoc experiment outputs.
- Why Now: `local_llm` now proves Ollama embeddings and planner JSON behavior, so the main remaining pre-integration gap is retrieval artifact shape: chunk fields, metadata, and failure/fallback expectations.
- Risk if Deferred: vector-index experiments or early `mirai` adapter work will invent retrieval contracts implicitly, increasing rework and seam drift across the two repos.

## Goal
Write a small, explicit retrieval artifact contract note in `local_llm` that records the minimum chunk, metadata, and fallback behavior expected from the first local retrieval path before any `mirai` provider adapter is started.

## Why this next
- Value: turns the remaining fuzzy retrieval seam into an executable handoff artifact for both future local experiments and the first `mirai` integration slice.
- Dependency/Risk: de-risks vector-index selection and provider handoff by making the expected retrieval output shape inspectable before code grows around it.
- Tech debt note: pays down the current implicit-contract debt without widening into implementation or benchmark work.

## Definition of Done
- [ ] A project-owned contract note documents the minimum retrieval artifact fields, metadata semantics, and fallback expectations for the first local retrieval path.
- [ ] The note distinguishes what belongs to `local_llm` versus what remains owned by `mirai` contract and policy layers.
- [ ] The note names open questions or deferred decisions separately from the first required contract so follow-on index/reranker work stays bounded.
- [ ] `README.md` or `agent_docs/README.md` links to the note if needed for discoverability.
- [ ] Tests/verification: review the note against current `local_llm` README/plans plus relevant `mirai` retrieval surfaces for consistency; no automated tests required for a docs-only slice.

## Scope
**In**
- Add one concise retrieval contract note under `agent_docs/`.
- Capture the first required chunk/result shape, metadata fields, and error/fallback expectations for local retrieval experiments.
- Clarify boundaries between local provider artifacts and `mirai`’s endpoint/policy ownership.
- Update lightweight planning/docs references if the new note should be discoverable from existing planning docs.

**Out**
- Any retrieval/index implementation.
- Any direct code changes in `../mirai`.
- Benchmarking, reranker evaluation, or provider wiring.

## Proposed approach
Use the current roadmap, debt log, Ollama baseline docs, and `mirai` retrieval seams as the source material for a short contract note that is concrete enough to guide future code but narrow enough to avoid premature design. Focus on the first local retrieval artifact only: chunk identity, source path, text/snippet expectations, score/ordering semantics, and fallback behavior when retrieval is unavailable or low-confidence. Explicitly separate required-now contract points from deferred choices like index backend, reranker usage, or richer telemetry.

## Steps (agent-executable)
1. Inspect the existing `local_llm` planning/docs and the relevant `mirai` retrieval shape to identify the smallest stable retrieval contract worth documenting now.
2. Write a concise retrieval artifact contract note under `agent_docs/` covering chunk/result fields, metadata, ordering/fallback expectations, and repo boundary ownership.
3. Call out what remains intentionally undecided so follow-on vector-index and reranker work does not inherit hidden scope.
4. Update any lightweight planning/doc references needed so the note is discoverable from the current repo guidance.
5. Re-read the note against existing local docs and `mirai` seams for consistency, then record any follow-on planning gaps in `backlog.md` or `tech_debt_log.md` only if needed.

## Risks / Tech debt / Refactor signals
- Risk: the note could accidentally over-specify future retrieval internals. -> Mitigation: document only the minimum external artifact contract needed for the next integration slices.
- Risk: the note could drift from `mirai` terminology or expectations. -> Mitigation: mirror existing seam language where possible and keep `mirai` ownership boundaries explicit.
- Debt: this slice leaves vector-index and ranking choices intentionally open.
- Refactor suggestion (if any): if multiple contract notes appear, group them under a small `agent_docs/contracts/` convention rather than scattering similar docs.

## Notes / Open questions
- Assumption: the next `mirai` adapter should target a narrow retrieval artifact contract, not a finalized local retrieval stack.
- Assumption: a docs-first slice is sufficient here because the open risk is contract ambiguity, not missing request reachability.
