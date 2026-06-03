#!/usr/bin/env bash
# heartbeat.sh start|end|tick - stamp WS/heartbeat so the supervisor can tell the loop is alive.
# Runs with cwd = workspace. Writes ./heartbeat and ./.loopcount.
set -uo pipefail

phase="${1:-tick}"
ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cnt_file=".loopcount"
cnt=0
[ -f "$cnt_file" ] && cnt="$(cat "$cnt_file" 2>/dev/null || echo 0)"

if [ "$phase" = "start" ]; then
  cnt=$((cnt + 1))
  echo "$cnt" > "$cnt_file"
fi

printf '%s %s %s\n' "$ts" "$cnt" "$phase" > heartbeat
