# Roadmap (Lightweight)

## Project Summary (North Star + Boundaries)

This project is the local-model proving ground for `mirai`'s self-hosted provider phase and future multi-model workflow routing. The near-term goal is not broad model experimentation; it is a reproducible local stack for RAG and planning workflows that preserves `mirai`'s existing provider seams, contract discipline, and capability-based model policy.

High-level goal:
- Deliver an Ollama-based local workflow for embeddings and planner-style generation that can later plug into `mirai` without changing MCP endpoint semantics, while producing evidence about which local models are suitable for each workflow capability.

Project boundaries:
- Preserve `mirai` as the owner of MCP contracts, safety policy, and endpoint semantics.
- Keep retrieval and planner/drafter model concerns as separate provider seams, matching the current `mirai` architecture.
- Treat local model size as an input to capability evidence, not as a public contract. Prefer recording whether a model supports capabilities such as strict JSON edit intents, single-note edits, or multi-step planning under bounded context.
- Favor small vertical slices that produce runnable artifacts over broad comparison docs or premature abstraction.
- Prefer runnable evidence that directly unblocks `mirai`'s next execution or retrieval slice over standalone support notes when the uncertainty can be captured in fixtures or smoke paths.
- Defer default-provider decisions in `mirai` until local parity expectations and failure behavior are documented here.

## Delivery Path

1. Ollama local provider baseline
- Stand up a repeatable Ollama workflow on the target workstation, with the runtime hosted on Windows and repo tooling kept in WSL2.
- Prove one chat/generation model and one embedding model can be invoked through stable local commands and documented config.

2. Embeddings-first RAG foundation
- Add a small local embeddings path aligned with `mirai`'s semantic retrieval seam.
- Capture chunking, request shape, and artifact expectations needed for later retrieval parity work.

3. Planner/drafter model baseline
- Add a planner-oriented local generation path that can return strict JSON for orchestration-style outputs.
- Record model sizing and latency tradeoffs on the target hardware for bounded-context use.
- Pivot draft generation away from model-authored unified diffs toward a strict `edit_intent` JSON response that mirrors the `mirai` contract once that contract is defined.
- Capture model-profile evidence for likely `mirai` gates such as `strict_json_edit_intent`, `single_note_edit`, and `multi_step_planning` without implying every local model should receive every workflow action.

4. Retrieval quality shaping
- Start with an exact local retrieval baseline using persisted embeddings and simple in-process ranking.
- Evaluate ANN/vector-index upgrades only after the exact baseline is working and measured against local workflow latency needs.
- Keep evaluation criteria tied to `mirai` retrieval contracts: bounded inputs, deterministic fallback, and inspectable result metadata.

5. Parity fixtures and failure contracts
- Build reusable prompt/retrieval fixtures that compare local-provider outputs against the current OpenAI-backed shapes.
- Prefer executable failure fixtures over prose-only notes when `mirai` needs bounded evidence about unavailable, overloaded, or malformed local runtime behavior.
- Keep fixtures useful for later request/session-level model selection by recording the model name, provider endpoint, capability under test, and expected failure interpretation.

6. `mirai` integration handoff
- Convert validated local stack decisions into narrow `mirai` cases for provider wiring.
- Keep integration slices small: retrieval seam first, planner seam second, workflow edit-intent evidence before any local draft/apply defaulting, model/profile selection only after capability evidence exists, and defaults only after parity evidence exists.

## Near-Term Success Criteria

- A documented Ollama setup runs locally with the expected model names, host/WSL split, and hardware assumptions.
- The repo contains a repeatable smoke path for local embeddings and planner-style generation calls.
- The next workflow-output slice proves the local model can return contract-shaped `edit_intent` JSON more reliably than unified diff text for the bounded note-update seam.
- Local smoke and fixture outputs identify which model/profile was exercised and which `mirai` capability gate it supports or fails.
- The next few slices should leave behind runnable evidence that `mirai` can consume directly, not just explanatory notes.
- Roadmap follow-ons are feature-led: local provider capability first, hardening and parity checks immediately after.
