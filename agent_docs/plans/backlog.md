# Backlog

## Next

1. Vector Index Choice + Benchmark
- Type: `feature`
- Value: chooses the first local vector store/index path using measured fit for the Ollama embeddings workflow.
- Size: ~1-2 days.

2. Reranker Evaluation Slice
- Type: `feature`
- Value: tests whether a small reranker materially improves result ordering enough to justify the extra moving part.
- Size: ~0.5-1 day.

## Later

1. Local Provider Parity Fixture Pack
- Type: `hardening`
- Value: creates reusable prompts and expected-shape checks for cross-provider comparisons.
- Size: ~1 day.

2. Mirai Semantic Provider Handoff Case
- Type: `feature`
- Value: converts the validated local retrieval stack into a narrow `mirai` implementation slice.
- Size: ~1 day.
