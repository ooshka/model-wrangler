# Backlog

## Now

1. Local Workflow Edit Intent Smoke Path
- Type: `feature`
- Value: proves the local workflow model can return strict `edit_intent` JSON aligned with the merged `mirai` draft contract, reducing the risk that self-hosted workflow execution stalls on malformed output shape.
- Size: ~1 day.

## Next

1. Local Retrieval Contract Exerciser
- Type: `feature`
- Value: turns the documented retrieval artifact contract into a small runnable check so later local retrieval changes cannot drift silently.
- Size: ~1 day.

2. Local Workflow Draft Reliability Fixture Pack
- Type: `hardening`
- Value: adds a small project-owned fixture set for malformed and near-miss `edit_intent` responses once the basic smoke path exists, so later local drafter tuning can be checked without live prompt guesswork.
- Size: ~1 day.

## Later

1. Windows Host Bootstrap Note Or Helper
- Type: `docs`
- Value: reduces workstation bring-up friction once the current Ollama baseline is stable enough to justify a tighter setup guide.
- Size: ~1 day.
