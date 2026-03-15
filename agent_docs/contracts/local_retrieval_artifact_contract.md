# Local Retrieval Artifact Contract

This note defines the minimum provider-side retrieval artifact shape that `local_llm` should preserve before a `mirai` adapter is added.

It is intentionally narrow:
- enough to guide local retrieval experiments
- enough to support a first adapter slice in `mirai`
- not a commitment to any specific index backend, reranker, or persistence format

## Purpose

`local_llm` should own the local-provider retrieval artifact produced after ranking.

`mirai` should continue to own:
- MCP endpoint shape and parameter validation
- policy and safety behavior
- error mapping and transport responses
- top-level response envelope fields such as `query` and `limit`
- public query chunk shaping such as wrapping grounding data under `metadata`

This note is only about the ranked chunk records the local retrieval path should be able to produce consistently.

## Required Chunk Artifact Shape

Each ranked retrieval result should be representable as a JSON object with these fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `path` | string | yes | Notes-root-relative path, using forward slashes. |
| `chunk_index` | integer | yes | Zero-based chunk position within the source note. |
| `content` | string | yes | Full chunk text used for retrieval and snippet derivation. |
| `score` | number | yes | Provider ranking score used only for ordering within the result set. |
| `snippet_offset` | object or `null` | yes | Offset into `content` for the best matching snippet when available. |

When `snippet_offset` is present, it should use:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `start` | integer | yes | Inclusive start offset in `content`. |
| `end` | integer | yes | Exclusive end offset in `content`. |

## Contract Semantics

- `path` must stay relative. Absolute paths and workstation-specific prefixes do not belong in the provider artifact.
- `chunk_index` is part of chunk identity. `path` plus `chunk_index` should uniquely identify a chunk inside one retrieval artifact set.
- `content` should contain the full retrieved chunk, not only a shortened preview.
- `score` is an ordering signal, not a stable cross-provider metric. Consumers may compare scores within one result set, but should not assume score parity across retrieval modes or providers.
- `snippet_offset` may be `null` when no reliable match span is available. When present, it must point to a valid slice inside `content`.
- Result ordering should already be ranked best-first by the provider path.

## Minimum Behavioral Expectations

- The first local retrieval path should return at most the requested limit after ranking.
- Zero-score or irrelevant chunks should not appear in the ranked output.
- Ties should resolve deterministically so repeated queries against the same artifact produce stable ordering.
- Path-prefix filtering, when used by a future adapter, should happen before ranking so only in-scope chunks are considered.
- If a persisted local index artifact exists, retrieval may use it; if not, retrieval may fall back to fresh indexing. This contract does not require one storage path over the other.

## Fallback and Failure Expectations

- Low-confidence retrieval should prefer returning an empty chunk list over fabricating records.
- Retrieval-unavailable conditions should be surfaced separately from chunk records. The chunk artifact itself should not encode transport or policy errors.
- A future `mirai` adapter may choose lexical fallback or another provider fallback path, but whichever path wins should still emit the same chunk artifact shape defined here.

## Boundary With `mirai`

The current observable `mirai` retrieval response shape adds envelope fields and a public grounding wrapper around ranked chunks:

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

For local planning purposes:
- `local_llm` should target the provider-side chunk artifact shape defined above, not the nested `metadata` wrapper used by `mirai`'s public query contract
- `mirai` should continue to own the envelope, query response shaping, request validation, and error response contract
- see [mirai_integration_constraints.md](./mirai_integration_constraints.md) for the current adapter-facing contract summary

## Explicitly Deferred

These decisions are intentionally left open for later slices:
- vector index backend or storage engine
- reranker adoption
- richer telemetry fields such as provider ID, latency, or retrieval mode provenance
- artifact versioning format for persisted local indexes
- score normalization across providers

## First Adapter Guidance

The first `mirai` adapter should assume only this:
- it can ask a local retrieval path for ranked chunk objects in the shape above
- it may need to wrap those chunk objects in the existing `mirai` envelope
- it should not depend yet on backend-specific metadata that is not listed in this note
