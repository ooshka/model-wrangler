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
- Impact: orchestration experiments may overfit to prompt hacks or model-specific behavior.
- Trigger: once the first planner model is callable locally.
- Planned handling: add a bounded planner JSON smoke slice and parity fixtures before treating local planning as integration-ready.
