#!/usr/bin/env python3
"""Objective goal gate. Prefer read-only goal.lock.json; fall back to goal.md YAML."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def utcnow():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def coerce(value):
    text = re.split(r"\s+#", value, maxsplit=1)[0].strip().strip('"').strip("'")
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    return int(text) if re.fullmatch(r"-?\d+", text) else text


def mini_yaml(block):
    data, criteria, cur, in_criteria = {}, [], None, False
    for raw in block.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent, text = len(raw) - len(raw.lstrip()), raw.strip()
        if indent == 0 and text.rstrip(":") == "criteria":
            in_criteria = True
            continue
        if indent == 0 and ":" in text:
            in_criteria = False
            key, _, value = text.partition(":")
            data[key.strip()] = coerce(value) if value.strip() else None
            continue
        if in_criteria:
            if text.startswith("- "):
                cur = {}
                criteria.append(cur)
                text = text[2:].strip()
            if cur is not None and ":" in text:
                key, _, value = text.partition(":")
                cur[key.strip()] = coerce(value)
    if criteria:
        data["criteria"] = criteria
    return data


def parse_yaml(block):
    spec = yaml.safe_load(block) if yaml else mini_yaml(block)
    if not isinstance(spec or {}, dict):
        raise ValueError("goal spec is not a mapping")
    return spec or {}


def load_spec(ws, goal_path, lock_path):
    if lock_path.exists():
        spec = json.loads(lock_path.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("goal.lock.json is not a JSON object")
        spec["_source"] = os.path.relpath(lock_path, ws)
        return spec

    text = goal_path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end < 0:
            raise ValueError("goal.md frontmatter not closed with ---")
        spec, source = parse_yaml(text[3:end].strip()), "frontmatter"
    else:
        match = re.search(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL)
        if not match:
            raise ValueError("no goal.lock.json and no YAML spec in goal.md")
        spec, source = parse_yaml(match.group(1)), "fenced-yaml"
    spec["_source"] = f"{os.path.relpath(goal_path, ws)}:{source}"
    return spec


def run(cmd, ws, timeout):
    try:
        proc = subprocess.run(cmd, shell=True, cwd=ws, capture_output=True, timeout=timeout)
        return proc.returncode, proc.stdout or b"", proc.stderr or b""
    except subprocess.TimeoutExpired:
        return 124, b"", b"timeout"
    except Exception as exc:  # noqa: BLE001
        return 125, b"", str(exc).encode()


def check(criterion, ws, default_timeout):
    result = {"id": criterion.get("id"), "desc": criterion.get("desc"), "passed": False}
    if not criterion.get("cmd"):
        result["error"] = "criterion has no cmd"
        return result, b"", b""

    rc, out, err = run(criterion["cmd"], ws, int(criterion.get("timeout", default_timeout)))
    got_sha = hashlib.sha256(out).hexdigest()
    result.update({
        "exit": rc, "stdout_sha256": got_sha,
        "stdout_tail": out[-400:].decode("utf-8", "replace"),
        "stderr_tail": err[-400:].decode("utf-8", "replace"),
    })

    checks = []
    if "expect_exit" in criterion:
        expected = int(criterion["expect_exit"])
        checks.append(("exit", rc == expected, f"{rc} vs {expected}"))
    if "expect_sha256" in criterion:
        expected = str(criterion["expect_sha256"]).lower()
        checks.append(("sha256", got_sha == expected, f"{got_sha} vs {expected}"))
    if "expect_regex" in criterion:
        regex = str(criterion["expect_regex"])
        checks.append(("regex", re.search(regex, out.decode("utf-8", "replace")) is not None, regex))
    if not checks:
        checks.append(("exit", rc == 0, f"{rc} vs 0"))
    result["checks"] = [{"kind": k, "ok": ok, "detail": d} for k, ok, d in checks]
    result["passed"] = all(ok for _, ok, _ in checks)
    return result, out, err


def write_proof(ws, verdict, outputs):
    proof_dir = ws / "derived" / "PROOF" / verdict["verified_at"].replace(":", "").replace("-", "")
    proof_dir.mkdir(parents=True, exist_ok=True)
    (proof_dir / "proof.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    for cid, (out, err) in outputs.items():
        (proof_dir / f"{cid}.stdout").write_bytes(out)
        (proof_dir / f"{cid}.stderr").write_bytes(err)
    verdict["proof_dir"] = str(proof_dir)


def emit(verdict, as_json, code):
    if as_json:
        print(json.dumps(verdict, indent=2))
    else:
        print(("DONE" if verdict["done"] else "NOT DONE") + f" - {verdict.get('reason') or verdict.get('error') or ''}".rstrip())
        for item in verdict["criteria"]:
            print(f"  [{'PASS' if item.get('passed') else 'FAIL'}] {item.get('id')}: {item.get('desc')}")
        if verdict.get("proof_dir"):
            print(f"  proof: {verdict['proof_dir']}")
    return code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", default=".", help="workspace dir (default: cwd)")
    ap.add_argument("--goal", help="goal.md path; defaults to WS/goal.md")
    ap.add_argument("--lock", help="goal.lock.json path; defaults to WS/goal.lock.json")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=900, help="per-criterion timeout in seconds")
    ap.add_argument("--no-proof", action="store_true")
    args = ap.parse_args()

    ws = Path(args.ws).resolve()
    verdict = {"done": False, "verifiable": False, "criteria": [], "verified_at": utcnow()}
    try:
        spec = load_spec(ws, Path(args.goal).resolve() if args.goal else ws / "goal.md",
                         Path(args.lock).resolve() if args.lock else ws / "goal.lock.json")
    except Exception as exc:  # noqa: BLE001
        verdict["error"] = f"could not load goal spec: {exc}"
        return emit(verdict, args.json, 2)

    verdict["spec_source"] = spec.get("_source")
    verdict["verifiable"] = bool(spec.get("verifiable", False))
    if not verdict["verifiable"]:
        verdict["reason"] = "soft mode: goal is not independently verifiable"
        return emit(verdict, args.json, 1)
    if not spec.get("criteria"):
        verdict["error"] = "verifiable:true but no criteria defined"
        return emit(verdict, args.json, 2)

    outputs = {}
    for criterion in spec["criteria"]:
        result, out, err = check(criterion, ws, args.timeout)
        verdict["criteria"].append(result)
        outputs[result.get("id") or f"C{len(outputs) + 1}"] = (out, err)
    verdict["done"] = (all if spec.get("require_all", True) else any)(c["passed"] for c in verdict["criteria"])
    if verdict["done"] and not args.no_proof:
        write_proof(ws, verdict, outputs)
    return emit(verdict, args.json, 0 if verdict["done"] else 1)


if __name__ == "__main__":
    sys.exit(main())
