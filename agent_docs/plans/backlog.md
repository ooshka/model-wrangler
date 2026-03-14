# Backlog

## Now

1. Planner JSON Smoke Path
- Type: `feature`
- Value: verifies the Ollama-backed planner path can return the strict JSON object shape `mirai` already normalizes for workflow orchestration.
- Size: ~0.5-1 day.

2. Local Retrieval Artifact Contract Note
- Type: `docs`
- Value: records the chunk, metadata, and fallback expectations needed before vector-index or `mirai` seam work begins.
- Size: ~0.5-1 day.

## Next

1. Reranker Evaluation Slice
- Type: `feature`
- Value: tests whether a small reranker materially improves result ordering enough to justify the extra moving part.
- Size: ~0.5-1 day.

2. Vector Index Choice + Benchmark
- Type: `feature`
- Value: chooses the first local vector store/index path using measured fit for the Ollama embeddings workflow.
- Size: ~1-2 days.

3. Mirai Integration Constraints Note
- Type: `docs`
- Value: records the exact provider-facing contracts `local_llm` must preserve when integration work starts.
- Size: ~0.5 day.

## Later

1. Local Provider Parity Fixture Pack
- Type: `hardening`
- Value: creates reusable prompts and expected-shape checks for cross-provider comparisons.
- Size: ~1 day.

2. Mirai Semantic Provider Handoff Case
- Type: `feature`
- Value: converts the validated local retrieval stack into a narrow `mirai` implementation slice.
- Size: ~1 day.
