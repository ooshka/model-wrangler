# Tech Debt Log

## Active structural debt

1. Local provider contract is still implicit
- Impact: embeddings and planner experiments could drift away from the seams `mirai` already exposes for retrieval and workflow planning.
- Trigger: becomes risky as soon as more than one runtime script or model-specific code path exists.
- Planned handling: keep early Cases focused on explicit local request/response contracts and config surfaces before any `mirai` wiring.

2. Retrieval stack shape is not selected yet
- Impact: chunk metadata, storage assumptions, and reranking hooks may be invented ad hoc during experimentation.
- Trigger: after the first embeddings smoke path lands.
- Planned handling: write a small retrieval artifact contract note before choosing a vector index or starting provider integration work.

3. Planner reliability beyond single-smoke coverage is still unproven locally
- Impact: one successful structured-output smoke path does not yet establish behavior across varied intents, larger contexts, or fallback scenarios.
- Trigger: becomes important once `mirai` adapter work or parity-fixture work is about to begin.
- Planned handling: keep the current planner JSON smoke as the baseline proof, then add parity fixtures or broader reliability checks only when they unblock concrete integration work.

4. Windows host bootstrap is still manual
- Impact: initial agent validation depends on Ollama being installed, running, and preloaded with the baseline models outside the repo.
- Trigger: when a fresh workstation or CI-like environment needs to reproduce the local baseline without prior host setup.
- Planned handling: consider a small host setup note or helper script once the first Ollama baseline smoke path is stable.
