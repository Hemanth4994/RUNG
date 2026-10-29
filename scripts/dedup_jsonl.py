"""Remove repeated rows (same "id") from a JSONL file, keeping the first one. Plain Python.

    python scripts/dedup_jsonl.py data/records_llm.jsonl --in-place
    python scripts/dedup_jsonl.py data/records_llm.jsonl --out data/records_llm_clean.jsonl

`--in-place` first copies the original to <name>.with_duplicates.jsonl (never overwriting an existing
copy), then rewrites the file. Works for issue files, prediction files and record files: all use "id".
A file with no repeated ids is left untouched.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil


def dedup_lines(lines: list[str]) -> tuple[list[str], int]:
    """Keep the first line for each id. Returns (kept lines, number removed). Blank lines are dropped."""
    seen: set = set()
    kept = []
    for line in lines:
        if not line.strip():
            continue
        key = json.loads(line)["id"]
        if key in seen:
            continue
        seen.add(key)
        kept.append(line.rstrip("\n"))
    removed = sum(1 for ln in lines if ln.strip()) - len(kept)
    return kept, removed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out")
    ap.add_argument("--in-place", action="store_true")
    a = ap.parse_args()
    if bool(a.out) == a.in_place:
        raise SystemExit("give exactly one of --out FILE or --in-place")

    with open(a.path, encoding="utf-8") as f:
        lines = f.readlines()
    kept, removed = dedup_lines(lines)
    print(f"{a.path}: {len(kept) + removed} rows, {len(kept)} unique ids, {removed} repeated rows removed")
    if removed == 0 and a.in_place:
        print("nothing to do; file left untouched")
        return
    if a.in_place:
        backup = a.path.rsplit(".jsonl", 1)[0] + ".with_duplicates.jsonl"
        if not os.path.exists(backup):
            shutil.copyfile(a.path, backup)
            print(f"original kept as {backup}")
        target = a.path
    else:
        target = a.out
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(kept) + "\n")


if __name__ == "__main__":
    main()
