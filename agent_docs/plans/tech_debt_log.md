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

3. Strict JSON planner reliability is unproven locally
- Impact: orchestration experiments may overfit to prompt hacks or model-specific behavior because the current baseline only proves freeform chat, not structured planner output.
- Trigger: active now; the first planner model is callable locally through the Ollama smoke path.
- Planned handling: validate the core workflow planner JSON shape in a bounded smoke slice first, then add parity fixtures only if the smoke path shows promising stability.

4. Windows host bootstrap is still manual
- Impact: initial agent validation depends on Ollama being installed, running, and preloaded with the baseline models outside the repo.
- Trigger: when a fresh workstation or CI-like environment needs to reproduce the local baseline without prior host setup.
- Planned handling: consider a small host setup note or helper script once the first Ollama baseline smoke path is stable.
