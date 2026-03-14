# local_llm

Experimental local model workspace for the self-hosted LLM phase of `mirai`.

## Purpose

This repository exists to evaluate and harden the local-model stack needed to support `mirai` without depending on hosted model providers.

Initial goals:
- identify a practical local LLM runtime for planning and patch-drafting workflows
- establish a local embedding and vector-index strategy that can support retrieval parity checks
- document operational constraints, configuration, and test workflows before wiring the provider into `mirai`

## Relationship to `mirai`

`mirai` remains the source of truth for MCP contracts, safety constraints, and provider-agnostic runtime seams.

This repository should focus on:
- local runtime setup and repeatable developer workflows
- provider experiments and comparison notes
- small integration slices that can later be consumed by `mirai`

This repository should not redefine `mirai` request/response contracts. Any contract changes should be planned in `mirai` first.

## Planning Docs

Project planning artifacts live under `agent_docs/`.

- `agent_docs/plans/roadmap.md`: short directional roadmap
- `agent_docs/plans/backlog.md`: candidate near-term slices
- `agent_docs/testing/README.md`: verification guidance for agents and contributors
