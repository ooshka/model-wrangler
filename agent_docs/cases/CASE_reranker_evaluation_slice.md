---
case_id: CASE_reranker_evaluation_slice
created: 2026-03-21
---

# CASE: Reranker Evaluation Slice

## Slice metadata
- Type: feature
- User Value: determines whether a small reranker materially improves local retrieval ordering enough to justify the added moving part before `mirai` consumes the self-hosted retrieval path.
- Why Now: the SQLite exact baseline and benchmark evidence are now in place, so the next concrete retrieval-quality question is whether a lightweight reranker changes result ordering enough to earn its operational cost.
- Risk if Deferred: the repo may either carry unnecessary reranker complexity into a later `mirai` handoff or skip a cheap quality win because no bounded comparison artifact exists.

## Goal
Add a small, repeatable reranker evaluation path that compares baseline exact-search ordering against one lightweight reranked variant on a project-owned fixture.

## Why this next
- Value: produces decision-grade evidence for whether reranking belongs in the near-term local retrieval stack.
- Dependency/Risk: sharpens the next `mirai` provider-handoff case by replacing hand-wavy reranker ideas with concrete ordering and latency evidence.
- Tech debt note: pays down the current “reranker is only a backlog idea” ambiguity while intentionally avoiding a full production reranker integration.

## Approach Outline

### Utility (Why this helps now)
- Creates one bounded evaluation artifact for local retrieval quality instead of folding reranker guesses into a later `mirai` adapter slice.
- Keeps the current exact-search baseline intact while making reranker adoption an evidence-based choice.

### Rationale (Why this approach)
- Prefer a fixture-backed comparison command over a broad model bakeoff, because the repo already has a canonical SQLite retrieval harness and needs a small yes/no signal rather than a new subsystem.
- Keep the reranker stage additive and optional after baseline ranking instead of rewriting retrieval internals; that isolates the quality question from storage/backend questions.
- Defer hosted or heavyweight reranker infrastructure for now. The narrow question is whether a simple local rerank pass moves the right chunks upward on representative inputs.

### Implementation Shape (How it will be done)
- Extend `scripts/retrieval/sqlite_exact.py` or a small adjacent helper with an optional rerank evaluation mode that compares baseline ordering against a lightweight rerank strategy on the same candidate set.
- Add one project-owned fixture under `agent_docs/testing/` that encodes a representative query where reranking plausibly helps or where “no improvement” is still informative.
- Add focused unit coverage in `tests/test_sqlite_exact_retrieval.py` for deterministic rerank output/summary shape without changing the existing baseline query contract.
- Document the evaluation command and interpretation in `agent_docs/testing/README.md`, then feed the result back into planning docs only if the slice reveals a clear next-step decision.

### Risk & Validation Preview
- Risk: the slice accidentally turns into a production reranker integration. Validation: keep the evaluation path separate from the default query behavior and avoid changing the existing artifact contract.
- Risk: the chosen fixture could overfit one anecdotal query. Validation: keep the fixture small but explicit about what ordering signal it is testing, and report comparison output rather than vague qualitative claims.
- Risk: rerank comparison output becomes nondeterministic or too ad hoc to guide planning. Validation: lock the result shape and expected ordering deltas in targeted unit tests.

## Definition of Done
- [ ] The repo has one repeatable reranker evaluation command or helper that compares baseline exact-search ordering against one lightweight reranked variant on a project-owned fixture.
- [ ] The evaluation output is bounded and documented, including enough information to tell whether reranking changed top-result ordering and what extra latency/cost it introduced.
- [ ] Existing exact-search behavior remains the baseline path; reranker evaluation does not silently change the default retrieval contract.
- [ ] Targeted unit tests cover the reranker evaluation result shape and deterministic ordering behavior for the chosen fixture.
- [ ] `agent_docs/testing/README.md` documents the canonical reranker evaluation command and how to read the result.
- [ ] Tests/verification: `python3 -m unittest tests.test_sqlite_exact_retrieval` and one documented reranker evaluation command under `scripts/retrieval/sqlite_exact.py`

## Scope
**In**
- A small fixture-backed reranker comparison path owned by the current SQLite retrieval harness.
- One lightweight rerank strategy suitable for evaluation on this workstation class.
- Focused tests and docs for the evaluation output.

**Out**
- Making reranking the default retrieval path.
- Adding hosted services, large model orchestration, or production-grade reranker serving.
- Changing `mirai` contracts or wiring.
- ANN/vector backend changes unrelated to reranker evaluation.

## Proposed approach
Keep the exact-search baseline as the control path and add one comparison-only reranker evaluation mode around it. Use the existing SQLite retrieval harness so the slice stays centered on current retrieval artifacts, candidate ordering, and benchmark-style output rather than inventing a new subsystem. The smallest useful implementation is to rank baseline candidates first, apply one deterministic lightweight rerank pass over the top candidate set, and emit a concise comparison summary with ordering deltas and timing. Keep the work localized to the retrieval script, its unit tests, and the testing docs so the next planner cycle can decide whether reranking should feed directly into a `mirai` handoff or be dropped.

## Steps (agent-executable)
1. Inspect the current SQLite retrieval script and tests to identify the narrowest seam for an optional post-ranking comparison mode.
2. Add one project-owned evaluation fixture that captures a representative query/candidate set where reranking can be meaningfully observed.
3. Implement a deterministic reranker evaluation path that compares baseline and reranked top results without changing the default query contract.
4. Add or update targeted unit tests for the comparison output shape, deterministic ordering, and “no default behavior change” expectations.
5. Update `agent_docs/testing/README.md` with the canonical reranker evaluation command and interpretation notes.
6. Record any clear follow-on decision in planning artifacts only if the slice conclusively points to adopting or rejecting reranking.

## Risks / Tech debt / Refactor signals
- Risk: evaluation-only code could still blur into production retrieval logic. -> Mitigation: keep the reranker path explicitly optional and comparison-oriented.
- Debt: this slice still leaves broader parity-fixture work and `mirai` provider handoff for later; it only answers whether reranking looks worth carrying forward.
- Refactor suggestion (if any): if post-ranking comparison logic grows beyond a few functions, extract a small retrieval-evaluation helper rather than overloading `sqlite_exact.py`.

## Notes / Open questions
- Assumption: one lightweight rerank strategy is enough for this decision slice; the repo does not need a multi-reranker bakeoff yet.
- Assumption: the evaluation output should optimize for planning clarity, not end-user API design.
