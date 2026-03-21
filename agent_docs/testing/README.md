# Testing Guide for LLM Agents

This document explains how to verify changes in `local_llm` with the smallest useful command set.

## Goal

Pick the narrowest verification that matches the change, then report exactly what was run and what passed or failed.

## Current State

- This repository is currently documentation-first.
- No application runtime or automated test suite has been established yet.
- Until code lands, docs-only changes typically require no automated verification.
- The current intended runtime split is: repo in WSL2, local model server on Windows.

## Expected Near-Term Upkeep

As local runtime scripts, config, or evaluation code are added:
- document the canonical setup command
- document the smallest smoke-test command
- document any required model/runtime prerequisites
- document whether the command should run in WSL2 or on the Windows host
- note when sandbox escalation or network access is required

## Minimal Command Selection by Change Type

- Docs-only changes:
  - Usually no tests required.
- New local runtime scripts:
  - Add at least one documented smoke command here.
- New evaluation harness or comparison code:
  - Add the narrowest reproducible verification command here before merging follow-on work.
- New local retrieval/index code:
  - Add focused unit tests for artifact shape, ranking behavior, and deterministic ordering.
  - Document one small benchmark command with a project-owned fixture when performance thresholds matter to follow-on planning.

## Current Ollama Baseline Verification

Windows host preconditions:
- Ollama installed and running on Windows.
- WSL2 mirrored networking enabled so the Windows localhost endpoint is reachable from WSL2 at `127.0.0.1`.
- Baseline models pulled on Windows:
  - `ollama pull qwen3:8b`
  - `ollama pull all-minilm`

WSL2 verification commands:
- Config sanity:
  - `python3 scripts/ollama/smoke.py --print-config`
- Smoke helper unit test:
  - `python3 -m unittest tests.test_ollama_smoke`
- Retrieval baseline unit test:
  - `python3 -m unittest tests.test_sqlite_exact_retrieval`
- Retrieval baseline benchmark helper:
  - `python3 -m scripts.retrieval.sqlite_exact --db-path /tmp/local_llm_retrieval.sqlite3 --fixture agent_docs/testing/sqlite_exact_benchmark_fixture.json`
- Runtime and model presence:
  - `python3 scripts/ollama/smoke.py --check-only`
- Planner JSON contract smoke:
  - `python3 scripts/ollama/smoke.py --planner-json-only`
- Full smoke path:
  - `python3 scripts/ollama/smoke.py`

Agent note:
- Local HTTP checks against the Windows-hosted Ollama runtime may require sandbox escalation in Codex even though they do not use the public internet.
- The default smoke config assumes `http://127.0.0.1:11434` from WSL2. Only add `config/ollama.env` overrides if this workstation uses a different Windows host address.

Expected result:
- `--check-only` returns JSON with `"status": "runtime-ready"`.
- `--planner-json-only` returns JSON with `"status": "planner-json-passed"` plus planner action count and first action name.
- The full smoke command returns JSON with `"status": "smoke-passed"` plus embedding dimensions, a chat preview, and planner JSON summary fields.
- The retrieval unit test passes with deterministic ranking and contract-shape checks.
- The retrieval benchmark helper prints JSON with `build_seconds`, `query_seconds`, and `top_result`.

Failure modes to report:
- `127.0.0.1:11434` unreachable from WSL2.
- One or both baseline models missing from the Windows-hosted Ollama instance.
- Planner JSON responses that are non-JSON, omit `rationale` or `actions`, or return invalid action payload types.
- Chat or embeddings requests returning non-JSON or empty payloads.
- Retrieval ranking returning zero-score chunks, unstable tie ordering, or malformed provider artifact fields.
