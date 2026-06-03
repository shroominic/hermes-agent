Load `auto-reverse-engineer`; read `references/kanban-runtime.md`,
`references/runtime-loop.md`, `references/re-phases.md`.

Slug: {{SLUG}} | WS: {{WS}} | target_type: {{TARGET_TYPE}}

Kanban goal-mode director, not tmux. Workspace is truth. Read `goal.lock.json`,
`goal.md`, `context.md`, `scope.txt`, `progress.md`, `paths.md`, `attempts.*`,
`inbox/REQUESTS.md`, `wiki/index.md`.

Do: work highest-value ready path; spawn child cards for parallel/specialized
work using tenant `{{SLUG}}` and workspace `dir:{{WS}}`; save evidence under
`derived/`; update wiki/attempts; run `python3 scripts/verify_goal.py --json`.

Human input: write `inbox/REQUESTS.md`, then `kanban_block`. Workers do not call
`clarify` or `send_message`.
