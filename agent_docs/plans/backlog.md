# Backlog

## Now

1. Retrieval Baseline Benchmark + Upgrade Thresholds
- Type: `feature`
- Value: measures whether the SQLite exact-search path is still acceptable before any ANN backend is introduced.
- Size: ~0.5-1 day.

## Next

1. Reranker Evaluation Slice
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
