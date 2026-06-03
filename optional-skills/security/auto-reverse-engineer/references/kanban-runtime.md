# Kanban Runtime

Kanban is the loop: liveness, retries, turns, child work, blocks, completion.
No tmux/cron supervisor.

## Launch Shape

```bash
hermes kanban create "Auto Reverse Engineer director: <slug>" \
  --assignee default --workspace "dir:<ws>" --tenant "<slug>" \
  --priority 2 --max-runtime 2h \
  --idempotency-key "auto-reverse-engineer:<slug>:director" \
  --skill auto-reverse-engineer --goal --goal-max-turns 20 \
  --body "<director instructions>"
```

Requires gateway `kanban.dispatch_in_gateway: true`.

## Roles

| Role | Must do |
|---|---|
| Director | Read workspace, choose highest-value ready path, spawn child cards, merge wiki/evidence, run verifier. |
| Child | Preserve `tenant`, `workspace_kind="dir"`, `workspace_path`, and RE skill unless a narrower skill is better. |
| Human block | Write exact ask to `inbox/REQUESTS.md`, call `kanban_block`, continue other ready paths. |

Use parent links for real dependencies. Complete only on verifier pass or human
confirmation of a soft goal.

## Monitor

```bash
hermes kanban list --tenant <slug>
hermes kanban watch --tenant <slug>
hermes kanban show <task_id> --json
```
