# Tech Debt Log

## Active structural debt

1. Local provider contracts are documented but not exercised by retrieval code yet
- Impact: the repo now has the right planning notes, but the eventual retrieval implementation could still drift if persistence, ranking, and adapter seams are not kept narrow.
- Trigger: becomes risky as soon as retrieval code lands or multiple local retrieval experiments appear.
- Planned handling: keep the first implementation focused on the existing provider artifact contract and avoid backend-specific contract leakage.

2. Retrieval quality beyond the exact-search baseline is still unproven
- Impact: the repo now has a working exact-search baseline, but retrieval-quality shaping beyond raw cosine ranking is still unproven before `mirai` handoff work.
- Trigger: active now that benchmark evidence exists and the next decision is whether a lightweight reranker materially improves result ordering.
- Planned handling: run one bounded reranker evaluation slice against the current SQLite retrieval harness before promoting any rerank-aware handoff work into `mirai`.

3. ANN upgrade threshold is not measured yet
- Impact: the team could either over-engineer a vector backend too early or cling to exact search after it stops fitting the workstation envelope.
- Trigger: now relevant as corpus size and latency evidence accumulates beyond the initial benchmark slice.
- Planned handling: use the canonical SQLite benchmark command to capture `chunk_count`, `note_count`, `artifact_bytes`, `build_seconds`, and `query_seconds`, then revisit ANN or a service-backed store when repeated representative runs exceed roughly `0.100s` query time, `1.000s` build time, or workstation-scale artifact/corpus bounds.

4. Planner reliability beyond single-smoke coverage is still unproven locally
- Impact: one successful structured-output smoke path does not yet establish behavior across varied intents, larger contexts, or fallback scenarios.
- Trigger: becomes important once `mirai` adapter work or parity-fixture work is about to begin.
- Planned handling: keep the current planner JSON smoke as the baseline proof, then add parity fixtures or broader reliability checks only when they unblock concrete integration work.

5. Windows host bootstrap is still manual
- Impact: initial agent validation depends on Ollama being installed, running, and preloaded with the baseline models outside the repo.
- Trigger: when a fresh workstation or CI-like environment needs to reproduce the local baseline without prior host setup.
- Planned handling: consider a small host setup note or helper script once the first Ollama baseline smoke path is stable.
