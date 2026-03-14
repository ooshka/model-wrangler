# Backlog

## Now

1. DMR Provider Baseline
- Type: `feature`
- Value: proves the local workstation can run the first chat and embedding models behind a repeatable Docker Model Runner workflow.
- Size: ~1 day.

2. Embeddings Smoke Path
- Type: `feature`
- Value: establishes the first local RAG building block and validates the request shape `mirai` will eventually consume.
- Size: ~0.5-1 day.

## Next

1. Planner JSON Smoke Path
- Type: `feature`
- Value: verifies a planner-oriented local model can return strict JSON reliably enough for orchestration experiments.
- Size: ~0.5-1 day.

2. Local Retrieval Artifact Contract Note
- Type: `docs`
- Value: records the chunk, metadata, and fallback expectations needed before vector-index or `mirai` seam work begins.
- Size: ~1 day.

3. Reranker Evaluation Slice
- Type: `feature`
- Value: tests whether a small reranker materially improves result ordering enough to justify the extra moving part.
- Size: ~0.5-1 day.

4. Mirai Integration Constraints Note
- Type: `docs`
- Value: records the exact provider-facing contracts `local_llm` must preserve when integration work starts.
- Size: ~0.5 day.

## Later

1. Vector Index Choice + Benchmark
- Type: `feature`
- Value: chooses the first local vector store/index path using measured fit for the DMR embeddings workflow.
- Size: ~1-2 days.

2. Local Provider Parity Fixture Pack
- Type: `hardening`
- Value: creates reusable prompts and expected-shape checks for cross-provider comparisons.
- Size: ~1 day.

3. Mirai Semantic Provider Handoff Case
- Type: `feature`
- Value: converts the validated local retrieval stack into a narrow `mirai` implementation slice.
- Size: ~1 day.
