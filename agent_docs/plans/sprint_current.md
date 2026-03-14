Active case: `CASE_planner_json_smoke_path`

Reason:
- The baseline Ollama slice already proves runtime reachability, embeddings, and freeform chat.
- The next highest-value local gap is structured planner output, because `mirai`'s workflow planner seam normalizes a strict JSON object with `rationale` and `actions`.
- This slice stays fully inside `local_llm` while reducing the main contract risk before retrieval/index selection grows the surface area.
