# Mirai Integration Constraints

This note records the current `mirai` retrieval query contract, workflow-model posture, and seam ownership that `local_llm` should preserve when local retrieval or workflow work resumes.

It is intentionally narrow:
- enough to keep local provider work aligned with `mirai`'s current public contract
- enough to guide the first `mirai` adapter slice
- not a replacement for the provider-side retrieval artifact contract in [local_retrieval_artifact_contract.md](./local_retrieval_artifact_contract.md)

## Purpose

`local_llm` should continue to own:
- local runtime setup, evaluation, and provider-side retrieval artifacts
- provider-specific retrieval behavior before adapter shaping
- experiments around index selection, reranking, and local operational constraints
- local workflow model capability evidence, including strict JSON behavior, bounded edit-intent drafting, latency, and failure modes

`mirai` should continue to own:
- MCP request and response contracts
- query result envelope shape
- policy, fallback, model/profile selection, and error mapping exposed at the API layer
- contract refactors when the public shape needs simplification

This note exists so future `local_llm` work targets the right boundary instead of preserving stale `mirai` response details.

## Current `mirai` Query Contract

The current observable `mirai` response for `GET /mcp/index/query` is:

```json
{
  "query": "alpha",
  "limit": 5,
  "chunks": [
    {
      "content": "alpha beta",
      "score": 1,
      "metadata": {
        "path": "root.md",
        "chunk_index": 0,
        "snippet_offset": {"start": 0, "end": 5}
      }
    }
  ]
}
```

Key constraints for `local_llm` planning:
- `metadata` is the canonical public grounding container for query results.
- `path`, `chunk_index`, and `snippet_offset` are no longer current top-level chunk fields in `mirai` query responses.
- `metadata.snippet_offset` may be `null` when no reliable lexical overlap span exists.
- `score` remains an ordering signal, not a cross-provider normalized metric.

## Adapter Boundary

For the next integration phase:
- `local_llm` should preserve ranked provider-side chunk artifacts in the shape defined by [local_retrieval_artifact_contract.md](./local_retrieval_artifact_contract.md).
- A `mirai` adapter may reshape those provider-side chunk fields into the current public MCP contract.
- `local_llm` should not treat the `mirai` MCP envelope or nested `metadata` wrapper as the provider-owned storage contract.
- `local_llm` should not add new public query fields on behalf of `mirai`.

## Workflow Model Boundary

For workflow planner/drafter evidence:
- `local_llm` should record the provider endpoint, model name, runtime settings, capability under test, latency envelope, and failure interpretation.
- Useful capability labels include `strict_json_edit_intent`, `single_note_edit`, `multi_step_planning`, `multi_note_plan`, and `large_context_synthesis`.
- Model size should be treated as evidence, not as a public contract gate. `mirai` may use a smaller local model for bounded stages and a stronger hosted model for broader planning in the same user session.
- Local workflow fixtures should validate provider-side output shape and failure categories. They should not assert `mirai` MCP error envelopes, approval policy, patch application behavior, or git/index side effects.
- If a local model cannot satisfy a capability reliably, record that as routing evidence rather than changing the shared `mirai` contract to fit that model.

## Early-Stage Contract Posture

`mirai` currently allows coordinated breaking contract changes when they remove ambiguity and the affected consumer set is still small.

For `local_llm`, that means:
- prefer matching the latest cleaner `mirai` contract over preserving stale compatibility assumptions
- do not assume additive compatibility layers are required during this phase
- record any proposed contract change in `mirai` first, then update local notes or fixtures to match

## Guidance For Follow-on Cases

Future `local_llm` slices should use this split:
- provider artifact questions: update or reference [local_retrieval_artifact_contract.md](./local_retrieval_artifact_contract.md)
- current `mirai` adapter/query contract questions: update or reference this note
- local workflow model capability questions: update this note or add focused executable fixtures that record model/profile evidence

If a future `mirai` contract refactor changes query shape again, update this note as part of the same planning cycle so local retrieval work does not drift.
