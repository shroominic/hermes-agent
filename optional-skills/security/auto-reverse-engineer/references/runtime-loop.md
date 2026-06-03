# Runtime Loop

Each Kanban turn treats cwd/`WS` as truth; no prior-turn memory.

## Startup

Read `goal.md`, `context.md`, `progress.md`, `attempts.md`, tail
`attempts.tsv`, `paths.md`, `wiki/index.md`, linked wiki pages, `inbox/`, and
inventories of `artifacts/`, `derived/`, `scripts/`. Rewrite `status.md` with
phase, next path, blockers, confidence.

## Turn

1. Orient: integrate answered inbox items; pick highest-value ready path.
2. Hypothesize: one or two sentences; mark unproven claims `[HYPOTHESIS]`.
3. Experiment: cheapest 15-30 minute test; static host-safe, dynamic Docker-only.
4. Record: save outputs under `derived/`/`logs/`, add evidence, update wiki,
   append `attempts.md` and `attempts.tsv`.
5. Re-rank: update `progress.md`/`paths.md`, block or abandon paths, write human
   asks, run `python3 scripts/verify_goal.py --json`.

## Attempt Row

`attempts.md`: timestamp, status, path, hypothesis, method, cited evidence,
outcome, artifacts, next.

`attempts.tsv`:
`attempt_id\tstatus\tconfidence\tcategory\thypothesis\tsummary\tartifacts`

## Parallelism and Inbox

Use child cards for independent binaries, function sets, hypotheses, or capture
families. Children keep same tenant/workspace. Director owns merges and final
verifier.

Human-only resource/decision: add dated request with exact `artifacts/` path and
unblocked path, mark path blocked, continue other ready work. If all paths are
blocked, write `status.md` and `inbox/REQUESTS.md`, then `kanban_block`.

## Stop Rules

Stop only on verifier pass, human-confirmed soft goal, human interruption
(`STOP`, block/archive/reassign), or allowed hard block. If stuck, re-read
evidence, lint wiki, or attack another layer.

Hard rules: no fabricated evidence/completion; do not modify `artifacts/`; no
target execution outside Docker/sandbox; no writes outside `WS`; retry only with
new evidence.
