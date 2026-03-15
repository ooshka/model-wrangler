# Agent Docs

Lightweight planning artifacts for incremental, agent-executable work in `local_llm`.

## Structure
- `cases/`: executable case files
- `contracts/`: local provider contract notes used before `mirai` adapter work
- `plans/backlog.md`: prioritized candidate slices
- `plans/roadmap.md`: short directional roadmap
- `testing/README.md`: testing infrastructure and verification commands for agents

Current contract note:
- `contracts/local_retrieval_artifact_contract.md`: minimum ranked chunk/result shape expected from the first local retrieval path
- `contracts/mirai_integration_constraints.md`: current `mirai` retrieval query contract and adapter-boundary expectations `local_llm` should preserve

## Scope

Use these docs to keep local-model evaluation work small, reviewable, and aligned with `mirai`'s provider-abstraction roadmap.

Current runtime assumption for planning:
- keep the repo and implementation workflow in WSL2
- prefer a Windows-hosted local runtime with an OpenAI-compatible API
- treat Ollama as the default local baseline unless a Case says otherwise
