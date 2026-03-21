# Tech Debt Log

## Active structural debt

1. Local provider contracts are documented but not exercised by retrieval code yet
- Impact: the repo now has the right planning notes, but the eventual retrieval implementation could still drift if persistence, ranking, and adapter seams are not kept narrow.
- Trigger: becomes risky as soon as retrieval code lands or multiple local retrieval experiments appear.
- Planned handling: keep the first implementation focused on the existing provider artifact contract and avoid backend-specific contract leakage.

2. Reusable parity evidence is still missing across retrieval and planner seams
- Impact: the repo now has benchmark, reranker, and planner smoke evidence, but follow-on `mirai` provider work would still rely on one-off command output instead of reusable local expectations.
- Trigger: active now that the next likely cross-repo handoff is planner/provider wiring rather than baseline capability proof.
- Planned handling: add one bounded parity-fixture pack plus validation helpers that capture retrieval artifact expectations, planner JSON structural expectations, and key failure categories.

3. ANN upgrade threshold is documented but not yet exercised against broader representative note sets
- Impact: the repo has an initial benchmark threshold, but future growth could still outpace the current single-fixture evidence if note volume or chunk variety changes materially.
- Trigger: becomes relevant when repeated representative runs move beyond the current project-owned benchmark fixture or when the next retrieval implementation slice starts stressing artifact size/latency bounds.
- Planned handling: keep the current threshold guidance as the baseline and revisit broader benchmark coverage only when corpus growth or `mirai` handoff pressure makes the single-fixture evidence insufficient.

4. Planner reliability beyond single-smoke coverage is still unproven locally
- Impact: one successful structured-output smoke path does not yet establish behavior across varied intents, larger contexts, or fallback scenarios.
- Trigger: becomes important once `mirai` adapter work or parity-fixture work is about to begin.
- Planned handling: keep the current planner JSON smoke as the baseline proof, then add parity fixtures or broader reliability checks only when they unblock concrete integration work.

5. Windows host bootstrap is still manual
- Impact: initial agent validation depends on Ollama being installed, running, and preloaded with the baseline models outside the repo.
- Trigger: when a fresh workstation or CI-like environment needs to reproduce the local baseline without prior host setup.
- Planned handling: consider a small host setup note or helper script once the first Ollama baseline smoke path is stable.
