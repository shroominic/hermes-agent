#!/usr/bin/env python3
"""Bootstrap a Kanban-backed auto-reverse-engineer workspace."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import sys

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
TEMPLATE_FILES = {
    "goal.md": "goal.md", "context.md": "context.md", "progress.md": "progress.md",
    "attempts.md": "attempts.md", "attempts.tsv": "attempts.tsv", "paths.md": "paths.md",
    "status.md": "status.md", "authorization.md": "authorization.md",
    "RUNTIME_PROMPT.md": "RUNTIME_PROMPT.md", "REQUESTS.md": "inbox/REQUESTS.md",
}
WIKI_FILES = ["index.md", "log.md", "facts.md", "hypotheses.md", "disproved.md"]
WIKI_SUBDIRS = ["entities", "concepts", "sources"]
RUNTIME_SCRIPTS = ["verify_goal.py", "heartbeat.sh", "re_evidence.py"]


def utcnow():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path):
    if not path:
        return {}
    data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        sys.exit("--answers must contain a JSON object")
    return data


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def substitute(src, dst, mapping):
    text = Path(src).read_text(encoding="utf-8")
    for key, value in mapping.items():
        text = text.replace("{{%s}}" % key, str(value))
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_text(text, encoding="utf-8")


def chmod_readonly(path):
    path = Path(path)
    if path.is_dir():
        for item in path.rglob("*"):
            item.chmod(0o555 if item.is_dir() else 0o444)
        path.chmod(0o555)
    else:
        path.chmod(0o444)


def copy_artifacts(paths, ws):
    scope = ["# In-scope artifact paths (one per line). Anything not listed is OUT of scope."]
    context = []
    for raw in paths:
        src = Path(raw).expanduser().resolve()
        if not src.exists():
            print(f"WARNING: artifact not found, skipping: {src}", file=sys.stderr)
            continue
        dst = ws / "artifacts" / src.name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            digest = "(directory)"
        else:
            shutil.copy2(src, dst)
            digest = sha256_file(dst)
        chmod_readonly(dst)
        rel = dst.relative_to(ws)
        scope.append(str(rel))
        context.append(f"- {rel} - {digest} - (added at bootstrap)")
    return scope, context


def kanban_command(slug, ws, assignee, max_runtime, goal_max_turns):
    body = (
        "Load the auto-reverse-engineer skill. Read RUNTIME_PROMPT.md, goal.lock.json, goal.md, "
        "context.md, scope.txt, paths.md, and wiki/index.md. Act as the director for this "
        "reverse-engineering project. Decompose ready paths into Kanban child tasks when useful, "
        f"and every child task MUST use tenant={slug!r}, workspace_kind='dir', workspace_path={str(ws)!r}. "
        "Run scripts/verify_goal.py --json before claiming completion. If blocked on human input, "
        "call kanban_block with the exact request and write it to inbox/REQUESTS.md."
    )
    parts = [
        "hermes", "kanban", "create", f"Auto Reverse Engineer director: {slug}",
        "--assignee", assignee, "--workspace", f"dir:{ws}", "--tenant", slug,
        "--priority", "2", "--max-runtime", max_runtime,
        "--idempotency-key", f"auto-reverse-engineer:{slug}:director",
        "--skill", "auto-reverse-engineer", "--goal", "--goal-max-turns", str(goal_max_turns),
        "--body", body,
    ]
    return " ".join(shlex.quote(str(p)) for p in parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="workspace root (e.g. ~/auto-reverse-engineer)")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--skill-dir", help="skill root; default = parent of this script's dir")
    ap.add_argument("--target-type", default="other", choices=["binary", "firmware", "mobile", "protocol", "other"])
    ap.add_argument("--goal", default="(fill in goal.md)")
    ap.add_argument("--artifact", action="append", default=[], help="immutable input; repeatable")
    ap.add_argument("--answers", help="optional JSON answers; CLI flags take precedence")
    ap.add_argument("--max-runtime", default="2h", help="Kanban per-task runtime cap")
    ap.add_argument("--goal-max-turns", type=int, default=20, help="Kanban goal-mode turn budget")
    ap.add_argument("--assignee", default="default", help="Hermes profile assigned to the director card")
    ap.add_argument("--force", action="store_true", help="overwrite an existing workspace")
    args = ap.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        sys.exit("slug must match ^[a-z0-9][a-z0-9-]{1,62}$")
    answers = read_json(args.answers)
    skill_dir = Path(args.skill_dir).expanduser().resolve() if args.skill_dir else Path(__file__).resolve().parents[1]
    tpl, scr = skill_dir / "templates", skill_dir / "scripts"
    if not tpl.is_dir():
        sys.exit(f"templates not found under {skill_dir}")

    ws = Path(args.root).expanduser().resolve() / "projects" / args.slug
    if ws.exists() and not args.force:
        sys.exit(f"workspace already exists: {ws} (use --force to overwrite)")
    target_type = args.target_type or answers.get("target_type", "other")
    goal = args.goal if args.goal != "(fill in goal.md)" else answers.get("goal", args.goal)
    mapping = {
        "SLUG": args.slug, "WS": ws, "TARGET_TYPE": target_type, "GOAL": goal,
        "DATE": dt.date.today().isoformat(), "MAX_RUNTIME": args.max_runtime,
        "GOAL_MAX_TURNS": args.goal_max_turns,
    }

    for sub in ["artifacts", "derived", "scripts", "logs", "inbox", "digests", "wiki"]:
        (ws / sub).mkdir(parents=True, exist_ok=True)
    for sub in WIKI_SUBDIRS:
        (ws / "wiki" / sub).mkdir(parents=True, exist_ok=True)
        (ws / "wiki" / sub / ".gitkeep").touch()
    for src, dst in TEMPLATE_FILES.items():
        substitute(tpl / src, ws / dst, mapping)
    for name in WIKI_FILES:
        substitute(tpl / "wiki-scaffold" / name, ws / "wiki" / name, mapping)
    for name in RUNTIME_SCRIPTS:
        dst = ws / "scripts" / name
        shutil.copy2(scr / name, dst)
        dst.chmod(0o755)

    scope, artifact_lines = copy_artifacts(list(answers.get("artifacts", [])) + args.artifact, ws)
    (ws / "scope.txt").write_text("\n".join(scope) + "\n", encoding="utf-8")
    (ws / "heartbeat").write_text(f"{utcnow()} 0 bootstrap\n", encoding="utf-8")
    if artifact_lines:
        ctx = ws / "context.md"
        ctx.write_text(ctx.read_text(encoding="utf-8").replace(
            "- (artifact - sha256 - note)",
            "\n".join(artifact_lines),
        ), encoding="utf-8")

    lock = {
        "version": 1, "slug": args.slug, "target_type": target_type,
        "verifiable": bool(answers.get("verifiable", False)),
        "require_all": bool(answers.get("require_all", True)),
        "criteria": answers.get("criteria", []), "created_at": utcnow(),
        "source": "bootstrap answers; edit only with explicit user approval",
    }
    lock_path = ws / "goal.lock.json"
    lock_path.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    lock_path.chmod(0o444)

    launch_cmd = kanban_command(args.slug, ws, args.assignee, args.max_runtime, args.goal_max_turns)
    launch_path = ws / f"launch-kanban-{args.slug}.sh"
    launch_path.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{launch_cmd}\n", encoding="utf-8")
    launch_path.chmod(0o755)

    print(f"workspace ready: {ws}\ngoal lock: {lock_path}\nlaunch helper: {launch_path}\n")
    print(f"# Start the Kanban runtime:\n{launch_cmd}\n")
    print(f"# Monitor:\nhermes kanban list --tenant {shlex.quote(args.slug)}")
    print(f"hermes kanban watch --tenant {shlex.quote(args.slug)}")


if __name__ == "__main__":
    main()
