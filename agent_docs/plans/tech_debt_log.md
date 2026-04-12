# Tech Debt

This file tracks current, unresolved technical debt that still affects planning or sequencing.
It is not intended to be a historical journal of every past planning discussion.

## Current Debt

### Retrieval Contract Coverage
- State: retrieval artifact expectations are documented, but the repo still lacks enough executable contract coverage to ensure later retrieval changes cannot drift silently.
- Impact: `mirai` handoff work would rely too much on prose contracts and one-off checks instead of durable verification.
- Trigger to fix: active now that retrieval contract exerciser work is near the top of the backlog.
- Likely next slice: `Local Retrieval Contract Exerciser`.

### Local Workflow Reliability Evidence
- State: the repo has baseline planner and `edit_intent` smoke coverage, but reliability beyond the happy-path smoke remains under-specified.
- Impact: future `mirai` provider work could over-trust limited runtime evidence for malformed, near-miss, or prompt-drift scenarios.
- Trigger to fix: before deeper workflow provider routing or stronger local-model claims are made.
- Likely next slice: `Local Workflow Draft Reliability Fixture Pack`.

### Planner Action Shape Alignment
- State: `mirai` now allows a smaller internal planner-side semantic draft action before normalizing back to canonical `workflow.draft_patch`, but `local_llm` does not yet explicitly track or validate that shape.
- Impact: planner prompts, docs, or fixtures here could drift from the planner-side contract `mirai` is now prepared to normalize.
- Trigger to fix: when touching planner prompts, fixtures, or planner capability evidence next.
- Likely next slice: `Local Planner Action Shape Alignment Note Or Fixture`.

### Model Capability Evidence Depth
- State: current smoke coverage proves baseline planner/drafter behavior, but it does not yet give a reusable capability matrix for choosing local models by named `mirai` capability.
- Impact: later model/profile routing decisions would still lean too heavily on anecdotal runs or raw model size assumptions.
- Trigger to fix: when `mirai` is ready to consume more explicit local capability evidence.
- Likely next slice: `Local Workflow Model Capability Matrix`.

### Windows Host Bootstrap
- State: workstation bring-up still depends on manual host-side Ollama setup outside the repo.
- Impact: fresh-machine setup remains more fragile than the project’s WSL-side tooling implies.
- Trigger to fix: when another workstation needs reproducible bring-up or local onboarding friction becomes material.
- Likely next slice: `Windows Host Bootstrap Note Or Helper`.

## Watchlist

### Benchmark Threshold Drift
- Current ANN upgrade thresholds are documented from a limited baseline.
- If corpus size, chunk diversity, or representative latency changes materially, revisit the benchmark evidence before assuming the current exact-SQLite path still fits.

### Retrieval Implementation Scope
- Keep the first local retrieval implementation narrow and contract-led.
- If provider-specific behavior starts leaking into storage, ranking, or response shaping, pause and reassert the contract boundary before expanding features.

### Fixture Sprawl
- Planner, retrieval, failure, and capability fixtures are all useful here, but they can sprawl quickly.
- If fixture count grows substantially, standardize naming/location/ownership rather than letting prompts, docs, and tests fragment.

## Recently Resolved

- Local workflow `edit_intent` smoke coverage now matches `mirai`’s current single-note draft contract instead of the older unified-diff assumption.
- Local planner, retrieval parity, and workflow failure fixtures are now present enough to support narrower next-step evidence work instead of baseline runtime bring-up.
