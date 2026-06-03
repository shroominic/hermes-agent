---
name: auto-reverse-engineer
description: |
  Use for authorized binary, firmware, mobile, BLE/RF, or protocol reverse
  engineering that should run as a durable Hermes Kanban project. Bootstraps an
  isolated workspace, locks any verifier, launches a goal-mode director, and
  uses child cards for parallel RE. Verifiable goals complete only via
  `goal.lock.json`; soft goals need human confirmation. Dynamic target execution
  must stay sandboxed.
version: 0.1.0
author: contact@shroominic.com
license: MIT
platforms: [linux, macos]
category: security
triggers:
  - "reverse engineer [target] in the background"
  - "set up an autonomous RE project for [target]"
  - "keep working on reversing [target] and update me"
  - "figure out the protocol/format of [target] on its own"
  - "run reverse engineering through kanban"
toolsets: [terminal, file, delegation, code_execution, kanban, messaging, web, clarify]
metadata:
  hermes:
    tags: [reverse-engineering, autonomous, background, kanban, binary-analysis, firmware, mobile, protocol]
    related_skills: [kanban-orchestrator, kanban-worker, oss-forensics, web-pentest]
---

# auto-reverse-engineer

Kanban-backed RE director for one authorized target. Workspace is
`WORKSPACE_ROOT/projects/<slug>`; Kanban, not tmux, owns lifecycle.

## Non-Negotiables

- Confirm authorization/scope first; refuse unclear scope.
- Treat workspace files as truth; cite every wiki fact to `artifacts/` or
  `derived/`.
- Keep child cards on the same tenant and `dir:<ws>` workspace.
- Run target code/tracing/fuzzing/emulation only in Docker/sandbox.
- Put human asks in `inbox/REQUESTS.md` and `kanban_block`.
- Complete verifiable goals only when `scripts/verify_goal.py --json` returns
  done from `goal.lock.json`.

## Bootstrap

Clarify once: target, goal, type, artifacts, live interaction, Docker, update
preference, stop policy, and any oracle. Then:

```bash
bash SKILL_DIR/scripts/install-re-tools.sh --check
python3 SKILL_DIR/scripts/bootstrap_workspace.py \
  --root "$WORKSPACE_ROOT" --slug "<slug>" --skill-dir "$SKILL_DIR" \
  --target-type "<binary|firmware|mobile|protocol|other>" \
  --goal "<one-line goal>" --artifact /abs/path/to/input.bin --assignee default
bash "$WS/launch-kanban-<slug>.sh"
```

Gateway requires `kanban.dispatch_in_gateway: true`.

## References

- `scope-authorization.md` - phase-0 gate.
- `kanban-runtime.md` - director, child cards, monitoring.
- `runtime-loop.md` - per-turn RE loop and stop rules.
- `re-phases.md` - target playbooks.
- `tool-matrix.md` - tools/fallbacks.
- `wiki-protocol.md` - durable cited memory.
- `monitor-and-goal.md` - verifier contract.
