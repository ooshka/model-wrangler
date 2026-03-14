# Testing Guide for LLM Agents

This document explains how to verify changes in `local_llm` with the smallest useful command set.

## Goal

Pick the narrowest verification that matches the change, then report exactly what was run and what passed or failed.

## Current State

- This repository is currently documentation-first.
- No application runtime or automated test suite has been established yet.
- Until code lands, docs-only changes typically require no automated verification.

## Expected Near-Term Upkeep

As local runtime scripts, config, or evaluation code are added:
- document the canonical setup command
- document the smallest smoke-test command
- document any required model/runtime prerequisites
- note when sandbox escalation or network access is required

## Minimal Command Selection by Change Type

- Docs-only changes:
  - Usually no tests required.
- New local runtime scripts:
  - Add at least one documented smoke command here.
- New evaluation harness or comparison code:
  - Add the narrowest reproducible verification command here before merging follow-on work.
