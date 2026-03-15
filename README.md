# local_llm

Experimental local model workspace for the self-hosted LLM phase of `mirai`.

## Purpose

This repository exists to evaluate and harden the local-model stack needed to support `mirai` without depending on hosted model providers.

Current workstation baseline:
- keep the repository, scripts, and agent workflow in WSL2
- run the local model runtime on the Windows host
- call the runtime from WSL2 through an OpenAI-compatible HTTP endpoint

Initial goals:
- identify a practical local LLM runtime for planning and patch-drafting workflows
- establish a local embedding and vector-index strategy that can support retrieval parity checks
- document operational constraints, configuration, and test workflows before wiring the provider into `mirai`

The current default runtime direction is Ollama on Windows, with `local_llm` owning the project-level config, smoke paths, and documentation consumed from WSL2.

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
- `agent_docs/contracts/mirai_integration_constraints.md`: current `mirai` retrieval query contract notes that local-provider work should preserve

## Local Runtime Direction

For this workstation class, prefer:
- repo and developer tooling in WSL2
- Ollama installed on Windows
- mirrored WSL2 networking so the Windows localhost endpoint is reachable from WSL2 at `127.0.0.1`
- local API access from WSL2 via `http://127.0.0.1:11434/v1`

This keeps the runtime path simple on Windows while preserving Linux-oriented tooling and shell workflows in the repository.

## Ollama Baseline

The current baseline models are:
- planner/chat: `qwen3:8b`
- embeddings: `all-minilm`

Configuration lives in `config/ollama.env.example`. Copy it to `config/ollama.env` only if you need workstation-specific overrides.

Networking assumption:
- WSL2 mirrored networking is enabled, so the Windows-hosted Ollama runtime is reachable from WSL2 at `127.0.0.1:11434`.
- If this workstation drifts from that setup, override `OLLAMA_BASE_URL` and `OLLAMA_OPENAI_BASE_URL` in `config/ollama.env`.

Windows host steps:
1. Install Ollama on Windows.
2. In Windows PowerShell, pull the baseline models:
   ```powershell
   ollama pull qwen3:8b
   ollama pull all-minilm
   ```
3. Confirm the runtime is serving:
   ```powershell
   curl http://127.0.0.1:11434/api/tags
   ```
   If this fails, start or restart the Ollama Windows app before moving on to the WSL2 smoke path.

WSL2 workflow:
1. Optionally copy the example config:
   ```bash
   cp config/ollama.env.example config/ollama.env
   ```
2. Inspect the effective local configuration:
   ```bash
   python3 scripts/ollama/smoke.py --print-config
   ```
3. Verify that WSL2 can reach the Windows-hosted runtime and that both models are present:
   ```bash
   python3 scripts/ollama/smoke.py --check-only
   ```
4. Run the strict planner JSON smoke path that mirrors `mirai`'s current workflow planner object shape:
   ```bash
   python3 scripts/ollama/smoke.py --planner-json-only
   ```
5. Run the full smoke path for embeddings, planner-style chat, and strict planner JSON:
   ```bash
   python3 scripts/ollama/smoke.py
   ```

The smoke script defaults already point at `127.0.0.1`, so most workstations should not need any local config override.
