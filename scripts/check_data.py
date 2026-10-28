"""Data-quality report for Rung files. Plain Python, no extra packages.

    python scripts/check_data.py issues data/issues.jsonl
    python scripts/check_data.py compare data/pred_baseline.jsonl data/pred_llm.jsonl

`issues`  : duplicates, missing fields, per-repo counts, label mix, date range.
`compare` : which ids are in one prediction file but not the other, and when those issues were
            created. This is the quickest way to explain a row-count mismatch between two runs.
"""
from __future__ import annotations

import json
import sys
from collections import Counter


def read(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def check_issues(rows: list[dict]) -> dict:
    ids = [r.get("id") for r in rows]
    counts = Counter(ids)
    dupes = {i: c for i, c in counts.items() if c > 1}
    dates = sorted(r["created_at"] for r in rows if r.get("created_at"))
    return {
        "rows": len(rows),
        "unique_ids": len(counts),
        "duplicate_ids": len(dupes),
        "extra_rows_from_duplicates": sum(c - 1 for c in dupes.values()),
        "missing_created_at": sum(1 for r in rows if not r.get("created_at")),
        "missing_human_labels": sum(1 for r in rows if not r.get("human_labels")),
        "per_repo": dict(Counter(str(r.get("id", "?")).rsplit("#", 1)[0] for r in rows)),
        "human_label_mix": dict(Counter(l for r in rows for l in r.get("human_labels", []))),
        "first_created": dates[0] if dates else None,
        "last_created": dates[-1] if dates else None,
    }


def compare_predictions(a: list[dict], b: list[dict]) -> dict:
    by_a = {r["id"]: r for r in a}
    by_b = {r["id"]: r for r in b}
    only_a = sorted(set(by_a) - set(by_b))
    only_b = sorted(set(by_b) - set(by_a))

    def span(ids, src):
        d = sorted(src[i]["created_at"] for i in ids)
        return (d[0], d[-1]) if d else None

    return {
        "rows_a": len(a), "unique_a": len(by_a),
        "rows_b": len(b), "unique_b": len(by_b),
        "only_in_a": only_a, "only_in_b": only_b,
        "only_in_a_created_between": span(only_a, by_a),
        "only_in_b_created_between": span(only_b, by_b),
    }


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "issues":
        print(json.dumps(check_issues(read(sys.argv[2])), indent=2))
    elif len(sys.argv) >= 4 and sys.argv[1] == "compare":
        print(json.dumps(compare_predictions(read(sys.argv[2]), read(sys.argv[3])), indent=2))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
