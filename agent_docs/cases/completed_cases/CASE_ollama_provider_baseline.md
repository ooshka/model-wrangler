---
case_id: CASE_ollama_provider_baseline
created: 2026-03-13
---

# CASE: Ollama Provider Baseline

## Slice metadata
- Type: feature
- User Value: creates the first runnable local provider baseline for the RAG and orchestration workflows this repo is meant to support.
- Why Now: model selection is no longer abstract; the project now has a concrete target stack shape based on a Windows-hosted Ollama runtime, separate embedding and planner seams, and the host hardware envelope.
- Risk if Deferred: follow-on retrieval and planner work will stay speculative, increasing the chance of writing docs or integration code against an unproven local runtime.

## Goal
Stand up a small Ollama baseline in `local_llm` that proves one embedding model and one planner-oriented generation model can be called locally through repeatable project-owned commands and documented configuration.

## Why this next
- Value: unlocks the first concrete local capability instead of adding more evaluation notes.
- Dependency/Risk: de-risks the next RAG and planner slices by making model names, invocation flow, and hardware assumptions explicit.
- Tech debt note: intentionally stops before vector-index selection or `mirai` provider wiring to keep the first slice small and reviewable.

## Definition of Done
- [ ] The repo contains a documented local Ollama workflow for this workstation class, with explicit host-vs-WSL responsibilities.
- [ ] One embedding model and one planner-oriented chat model are configured as the project baseline with explicit model identifiers.
- [ ] A repeatable smoke path exercises the local embeddings API and a planner-style chat completion/API call without relying on hosted services.
- [ ] `agent_docs/testing/README.md` describes how to run the smoke path and any required preconditions or hardware assumptions.
- [ ] Tests/verification: execute the documented local smoke commands and any project checks needed for new scripts/config docs.

## Scope
**In**
- Add project-owned runtime/config assets needed to use Ollama locally from the WSL2 workspace.
- Choose and document the initial baseline models for embeddings and planner-style generation.
- Add one small smoke workflow proving both API surfaces are reachable and usable locally.
- Update testing/docs so another agent can reproduce the baseline without re-planning.

**Out**
- Vector database or index selection.
- Reranker integration.
- Direct changes to `../mirai`.
- Planner prompt tuning or contract-parity fixture work beyond a minimal smoke check.

## Proposed approach
Use Ollama as the baseline local runtime because it fits the Windows-plus-WSL2 workstation target while still exposing OpenAI-compatible chat and embeddings surfaces to the repo. Keep the first slice narrow: project-owned setup/config documentation, explicit baseline model identifiers, and one smoke workflow that proves local calls succeed from WSL2 against the Windows-hosted runtime. Prefer a planner-oriented coding/general model in the 7B-class range and a small embedding model so the baseline fits the hardware envelope before any quality tuning or vector-store choices.

## Steps (agent-executable)
1. Inspect the current repo for any existing script or config conventions that should own the Ollama baseline.
2. Add the minimal local runtime assets needed to use a Windows-hosted Ollama runtime from this project, keeping host assumptions explicit and secrets out of repo files.
3. Introduce a small project-level configuration surface for the chosen baseline model identifiers and local API endpoint defaults.
4. Add a smoke script or equivalent repeatable command path that calls the local embeddings API and a planner-style chat completion API.
5. Update `README.md` and `agent_docs/testing/README.md` with setup, invocation, and verification guidance for the new baseline.
6. Run the documented smoke path and any lightweight repo checks needed to prove the new assets are coherent.
7. Record any follow-on gaps discovered during validation in `agent_docs/plans/backlog.md` or `agent_docs/plans/tech_debt_log.md` without widening this Case.

## Risks / Tech debt / Refactor signals
- Risk: chosen baseline models may not fit acceptably on the target GPU/RAM combination. -> Mitigation: keep the first slice on a small embedding model and a conservative planner model, and document fallback sizing notes.
- Risk: Windows-hosted runtime access from WSL2 may vary across workstation networking setups. -> Mitigation: keep setup guidance explicit, prefer the standard localhost path first, and validate only the local workstation path in this slice.
- Debt: this slice introduces runtime-specific startup and smoke assets before a stable abstraction exists for future runtimes.
- Refactor suggestion (if any): if more than one smoke path appears, extract shared request helpers instead of duplicating command logic across scripts.

## Notes / Open questions
- Assumption: Ollama is the selected local runtime for the first delivery phase rather than an option under comparison.
- Assumption: the first baseline optimizes for operational fit and reproducibility, not best-possible model quality.
