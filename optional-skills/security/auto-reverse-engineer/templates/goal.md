---
goal_id: {{SLUG}}
target_type: {{TARGET_TYPE}}
verifiable: false
require_all: true
criteria: []
---

# Goal - {{SLUG}}

- target: {{TARGET_TYPE}}
- end goal: {{GOAL}}
- created: {{DATE}}
- locked verifier: `goal.lock.json`

## Verify

`verify_goal.py` reads read-only `goal.lock.json` before this file. Prose cannot
complete verifiable goals. With explicit approval, a later oracle can set:

```json
{
  "version": 1,
  "slug": "{{SLUG}}",
  "target_type": "{{TARGET_TYPE}}",
  "verifiable": true,
  "require_all": true,
  "criteria": [
    {
      "id": "C1",
      "desc": "Parser round-trips held-out captures",
      "cmd": "python3 derived/parse.py --selftest artifacts/holdout/",
      "expect_exit": 0
    }
  ]
}
```

## Constraints

- In-scope artifacts only; see `scope.txt`.
- Dynamic target execution: Docker/sandbox only.
- Additional limits: `authorization.md`.

## Budget

- max runtime: {{MAX_RUNTIME}}
- goal turns: {{GOAL_MAX_TURNS}}

Soft mode (`verifiable:false`) needs human confirmation.
