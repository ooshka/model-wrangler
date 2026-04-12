# Backlog

## Now

No currently tracked items.

## Next

1. Local Retrieval Contract Exerciser
- Type: `feature`
- Value: turns the documented retrieval artifact contract into a small runnable check so later local retrieval changes cannot drift silently.
- Size: ~1 day.

2. Local Workflow Draft Reliability Fixture Pack
- Type: `hardening`
- Value: adds a small project-owned fixture set for malformed and near-miss `edit_intent` responses once the basic smoke path exists, so later local drafter tuning can be checked without live prompt guesswork.
- Size: ~1 day.

3. Local Workflow Model Capability Matrix
- Type: `feature`
- Value: records runnable smoke evidence for local workflow models by named `mirai` capability, so later `mirai` model/profile routing can choose a local model for the safe subset without relying on raw model size.
- Size: ~1 day.

4. Local Planner Action Shape Alignment Note Or Fixture
- Type: `hardening`
- Value: tracks the new `mirai` planner-side semantic `draft_note` action shape so local planner prompts, notes, or fixtures do not drift from the contract that `mirai` now normalizes server-side into canonical `workflow.draft_patch` actions.
- Size: ~0.5 day.

## Later

1. Windows Host Bootstrap Note Or Helper
- Type: `docs`
- Value: reduces workstation bring-up friction once the current Ollama baseline is stable enough to justify a tighter setup guide.
- Size: ~1 day.
