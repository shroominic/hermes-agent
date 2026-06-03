#!/usr/bin/env python3
"""Artifact/evidence ledger for an auto-reverse-engineer workspace."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

DEFAULT_STORE = Path("derived/evidence.json")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load(store):
    return json.loads(store.read_text()) if store.exists() else {"items": []}


def save(store, data):
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2), encoding="utf-8")


def cmd_add(args):
    if not (args.path or args.value):
        sys.exit("add requires --path or --value")
    data = load(args.store)
    item = {
        "id": args.id or f"EV-{len(data['items']) + 1:04d}",
        "type": args.type,
        "source": args.source,
        "note": args.note,
        "added": now(),
    }
    if args.path:
        item["path"] = args.path
        path = Path(args.path)
        item["sha256"] = sha256_file(path) if path.exists() else None
    if args.value:
        item["value"] = args.value
    data["items"].append(item)
    save(args.store, data)
    print(f"added {item['id']} ({args.type})")


def cmd_list(args):
    for item in load(args.store)["items"]:
        if args.type and item.get("type") != args.type:
            continue
        ref = item.get("path") or item.get("value") or ""
        print(f"{item['id']}\t{item.get('type')}\t{ref}\t{item.get('sha256') or ''}")


def cmd_verify(args):
    bad = 0
    for item in load(args.store)["items"]:
        path, recorded = item.get("path"), item.get("sha256")
        if not path or recorded is None:
            continue
        if not Path(path).exists():
            print(f"MISSING {item['id']} {path}")
            bad += 1
        elif (current := sha256_file(path)) != recorded:
            print(f"DRIFT   {item['id']} {path} (recorded {recorded[:12]} now {current[:12]})")
            bad += 1
    print(f"verify: {bad} problem(s)")
    sys.exit(1 if bad else 0)


def cmd_summary(args):
    items, by_type = load(args.store)["items"], {}
    for item in items:
        by_type[item.get("type")] = by_type.get(item.get("type"), 0) + 1
    print(f"evidence items: {len(items)}  by_type={by_type}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", type=Path, default=DEFAULT_STORE)
    sub = ap.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add")
    for name in ("type", "path", "value", "source", "note", "id"):
        add.add_argument(f"--{name}", required=(name == "type"))
    add.set_defaults(func=cmd_add)

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--type")
    list_cmd.set_defaults(func=cmd_list)

    sub.add_parser("verify").set_defaults(func=cmd_verify)
    sub.add_parser("summary").set_defaults(func=cmd_summary)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
