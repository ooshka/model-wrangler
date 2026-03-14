# Roadmap (Lightweight)

## Project Summary (North Star + Boundaries)

This project is the local-model proving ground for `mirai`'s self-hosted provider phase. The near-term goal is not broad model experimentation; it is a reproducible local stack for RAG and planning workflows that preserves `mirai`'s existing provider seams and contract discipline.

High-level goal:
- Deliver a Docker Model Runner based local workflow for embeddings and planner-style generation that can later plug into `mirai` without changing MCP endpoint semantics.

Project boundaries:
- Preserve `mirai` as the owner of MCP contracts, safety policy, and endpoint semantics.
- Keep retrieval and planner/drafter model concerns as separate provider seams, matching the current `mirai` architecture.
- Favor small vertical slices that produce runnable artifacts over broad comparison docs or premature abstraction.
- Defer default-provider decisions in `mirai` until local parity expectations and failure behavior are documented here.

## Delivery Path

1. DMR local provider baseline
- Stand up a repeatable Docker Model Runner workflow on the target workstation.
- Prove one chat/generation model and one embedding model can be invoked through stable local commands and documented config.

2. Embeddings-first RAG foundation
- Add a small local embeddings path aligned with `mirai`'s semantic retrieval seam.
- Capture chunking, request shape, and artifact expectations needed for later retrieval parity work.

3. Planner/drafter model baseline
- Add a planner-oriented local generation path that can return strict JSON for orchestration-style outputs.
- Record model sizing and latency tradeoffs on the target hardware for bounded-context use.

4. Retrieval quality shaping
- Evaluate optional reranking and vector-index choices only after the embeddings baseline is working.
- Keep evaluation criteria tied to `mirai` retrieval contracts: bounded inputs, deterministic fallback, and inspectable result metadata.

5. Parity fixtures and failure contracts
- Build reusable prompt/retrieval fixtures that compare local-provider outputs against the current OpenAI-backed shapes.
- Document expected fallback behavior when local models are unavailable, overloaded, or misconfigured.

6. `mirai` integration handoff
- Convert validated local stack decisions into narrow `mirai` cases for provider wiring.
- Keep integration slices small: retrieval seam first, planner seam second, defaults only after parity evidence exists.

## Near-Term Success Criteria

- A documented DMR setup runs locally with the expected model names and hardware assumptions.
- The repo contains a repeatable smoke path for local embeddings and planner-style generation calls.
- Roadmap follow-ons are feature-led: local provider capability first, hardening and parity checks immediately after.
