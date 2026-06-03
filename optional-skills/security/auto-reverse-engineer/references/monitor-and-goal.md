# Monitor and Goal Gate

Kanban owns lifecycle; `verify_goal.py` owns verifiable completion.

## Workspace Signals

- `status.md`: latest state
- `progress.md`: phase, confidence, milestones
- `attempts.md` / `attempts.tsv`: experiment ledger
- `inbox/REQUESTS.md`: human asks
- `derived/PROOF/<ts>/`: verifier proof

## Goal Rules

- Verifier reads read-only `goal.lock.json` before `goal.md`.
- Soft spec: `{"verifiable": false, "criteria": []}` never auto-passes; set
  `goal_candidate: true`, cite evidence, then block for human review.
- Verifiable spec runs criteria in workspace; checks may include `expect_exit`,
  `expect_sha256`, `expect_regex`.
- Done: `kanban_complete` with proof path.
- Not done: continue or spawn child cards.
- Missing human resource: append inbox request, then `kanban_block`.

Minimal criterion:

```json
{"id":"C1","cmd":"python3 derived/parse.py --selftest artifacts/holdout/","expect_exit":0}
```
