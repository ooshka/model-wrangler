---
case_id: CASE_sqlite_exact_retrieval_baseline
created: 2026-03-21
---

# CASE: SQLite Exact Retrieval Baseline

## Slice metadata
- Type: feature
- User Value: gives the repo a first local retrieval path that is easy to inspect, easy to persist, and exact enough to validate chunking and adapter behavior before heavier indexing work begins.
- Why Now: the Ollama embedding path and retrieval artifact contract already exist, so the next meaningful decision is the first concrete retrieval implementation shape rather than more abstract vector-store comparison.
- Risk if Deferred: the repo will keep talking about retrieval, reranking, and `mirai` handoff without proving a smallest working local search path or locking in the operational tradeoffs that matter on this workstation.

## Goal
Adopt a SQLite-backed exact cosine retrieval baseline as the first local vector path, with ANN and service-backed stores deferred until measured corpus size or latency makes them necessary.

## Why this next
- Value: turns the current vector-store question into a small executable slice instead of a broad infrastructure choice.
- Dependency/Risk: unblocks the first retrieval implementation while preserving the provider artifact contract already documented under `agent_docs/contracts/`.
- Tech debt note: intentionally avoids early ANN and database-service complexity; if the corpus or latency envelope grows, that tradeoff must be revisited with measurements rather than intuition.

## Definition of Done
- [ ] A planner-owned note or implementation-ready plan states that the first local retrieval path stores chunk metadata in SQLite and performs exact cosine ranking over persisted embeddings.
- [ ] The Case defines the minimum benchmark inputs and measurements needed to prove the baseline is acceptable on this workstation before any ANN follow-up is opened.
- [ ] The Case documents explicit upgrade triggers for revisiting Faiss/HNSW or a service-backed vector store.
- [ ] Tests/verification: re-read the Case against `README.md`, `agent_docs/contracts/local_retrieval_artifact_contract.md`, and the current backlog/roadmap to confirm the decision stays within repo boundaries; no automated tests required for this planning slice.

## Scope
**In**
- Choose the first local retrieval/index strategy for this repo.
- Constrain the first implementation to an in-process, inspectable, exact-search path.
- Define benchmark and upgrade-trigger expectations for later ANN evaluation.
- Update planner artifacts so follow-on work implements the chosen path rather than reopening the decision.

**Out**
- Implementing the retrieval code itself.
- Adding Faiss, HNSW, Qdrant, Chroma, or another vector service in this slice.
- Reranker evaluation.
- Any direct changes in `../mirai`.

## Proposed approach
Treat the current repository state as a small-repo retrieval problem, not a production-scale vector-database problem. Persist chunk metadata plus embeddings in a local SQLite artifact, then do exact cosine ranking in-process for the first retrieval slice. This preserves determinism, inspectability, and low operational overhead while matching the documented chunk contract. Capture simple benchmark checks in the follow-on implementation: index build time, query latency, and stable ranked outputs on a small representative note set. Revisit ANN only if measured latency, corpus size, or memory pressure becomes a concrete problem.

## Steps (agent-executable)
1. Implement a local chunk + embedding persistence format centered on SQLite tables and repo-relative paths.
2. Add exact cosine query ranking over stored embeddings, returning ranked chunk artifacts in the existing provider contract shape.
3. Record baseline measurements for index build and query latency on a representative local note set.
4. Open a separate ANN follow-up only if the measured baseline misses the agreed thresholds or the corpus shape changes materially.

## Risks / Tech debt / Refactor signals
- Risk: the exact-search baseline could feel slow once the corpus grows beyond the early workstation-sized target. → Mitigation: treat latency and corpus-size thresholds as explicit upgrade triggers, not implicit dissatisfaction.
- Risk: storing vectors outside a purpose-built ANN library could invite a later migration cost. → Mitigation: keep the provider artifact contract backend-agnostic and isolate persistence/ranking behind one local retrieval seam.
- Debt: this choice defers ANN and richer filtering capabilities in exchange for a faster path to a correct first retrieval stack.
- Refactor suggestion (if any): when retrieval code lands, keep chunking, embedding generation, persistence, and ranking as separate modules so a later Faiss/HNSW swap does not force contract churn.

## Notes / Open questions
- Assumption: the near-term corpus is small enough that exact search is acceptable on the target workstation.
- Upgrade trigger candidates: sustained query latency outside the acceptable local workflow envelope, significant corpus growth, or the need for ANN-specific filtering/scale behavior.
