# Roadmap

## North Star

`local_llm` is the local-model proving ground for `mirai`'s self-hosted provider phase. Its job is not broad model experimentation; it should produce runnable evidence about which local runtime, retrieval, and workflow-generation paths can satisfy named `mirai` capabilities without redefining `mirai` contracts.

## Current Milestone

### Self-Hosted Provider Confidence

Outcome: `local_llm` has enough executable retrieval, workflow, failure, and capability evidence for `mirai` to make concrete local-provider routing decisions without guessing from one-off smoke runs or prose-only notes.

Exit criteria:
- [ ] Local retrieval artifact expectations are covered by a runnable contract exerciser that validates shape, metadata, ranking assumptions, and failure interpretation owned by `local_llm`.
- [ ] Workflow edit-intent reliability has fixture coverage for malformed and near-miss local model responses without requiring live prompt guesswork.
- [ ] A capability matrix records model/runtime evidence for at least `strict_json_edit_intent`, `single_note_edit`, and `multi_step_planning`.
- [ ] Planner-side action-shape evidence tracks the current `mirai` semantic draft action shape before normalization to canonical `workflow.draft_patch`.
- [ ] The README or testing guide identifies which evidence is ready for `mirai` consumption and which claims remain unproven.

## Milestone Ladder

1. Runtime Baseline
- Owner: `local_llm`
- Purpose: establish repeatable Ollama-on-Windows, WSL2 tooling, chat/generation, embeddings, and smoke commands.
- Exit: baseline model names, host/WSL networking, config, and smoke paths are documented and runnable.

2. Retrieval Contract Evidence
- Owner: `local_llm`
- Purpose: prove local retrieval artifacts can support `mirai`'s provider seam without silently drifting in shape, ranking, or failure behavior.
- Exit: retrieval contract exerciser and fixtures produce deterministic pass/fail evidence.

3. Workflow Capability Evidence
- Owner: `local_llm`
- Purpose: measure local workflow models by named `mirai` capabilities rather than raw model size.
- Exit: capability matrix and fixture pack identify which local models can safely handle bounded planner/drafter stages and which require hosted escalation.

4. Integration Handoff
- Owner: `local_llm`, consumed by `mirai`
- Purpose: convert local-provider evidence into concrete `mirai` provider wiring and profile-routing decisions.
- Exit: `mirai` can cite local retrieval/workflow fixtures and capability evidence when implementing local provider profiles.

## Cross-Repo Contract

- `mirai` owns MCP/API contracts, safety policy, workflow semantics, provider/profile policy, audit shape, and product behavior.
- `local_llm` owns local runtime setup, smoke paths, retrieval artifacts, model capability evidence, and provider-side failure interpretation.
- Handoff rule: do not change `mirai` endpoint semantics here; produce evidence and fixtures that let `mirai` make the contract or routing decision.
- Capability rule: record model name, runtime endpoint/settings, capability under test, latency envelope when relevant, output shape, and failure mode.

## Next Slices

1. Local Retrieval Contract Exerciser
- Repo: `local_llm`
- Advances: Self-Hosted Provider Confidence and Retrieval Contract Evidence
- Why next: the retrieval artifact contract is documented, but later local retrieval work still needs executable drift protection.

2. Local Workflow Draft Reliability Fixture Pack
- Repo: `local_llm`
- Advances: Self-Hosted Provider Confidence and Workflow Capability Evidence
- Why next: happy-path edit-intent smoke exists, but malformed and near-miss local outputs need reusable fixture coverage before `mirai` relies on the local drafter.

3. Local Workflow Model Capability Matrix
- Repo: `local_llm`
- Advances: Workflow Capability Evidence and Integration Handoff
- Why next: `mirai` needs capability-level evidence for profile routing; raw model size and anecdotal smoke results are not enough.

4. Local Planner Action Shape Alignment Note Or Fixture
- Repo: `local_llm`
- Advances: Integration Handoff
- Why next: `mirai` now supports a smaller semantic planner action before canonical normalization, and local prompts/fixtures should not drift from that boundary.
