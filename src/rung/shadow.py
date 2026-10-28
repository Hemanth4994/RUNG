"""Shadow mode: the agent proposes a label for every issue, but nothing is acted on.
We compare each proposal with what the maintainers really did and keep the outcome.

    python -m rung.shadow data/issues.jsonl --predictor baseline \
        --out data/pred_baseline.jsonl --records data/records_baseline.jsonl

Predictions are appended one at a time, so an interrupted run resumes without re-spending API calls.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import Callable, Iterable

from .records import Record, save_records
from .taxonomy import COARSE

Predictor = Callable[[str, str], str]  # (title, body) -> one of COARSE


def load_issues(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _done_ids(out_path: str) -> set[str]:
    if not os.path.exists(out_path):
        return set()
    with open(out_path, encoding="utf-8") as f:
        return {json.loads(line)["id"] for line in f if line.strip()}


def run_shadow(issues: Iterable[dict], predict: Predictor, out_path: str, limit: int | None = None) -> int:
    """Predict for each issue not already in out_path. Returns number of new predictions."""
    done = _done_ids(out_path)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    new = 0
    with open(out_path, "a", encoding="utf-8") as f:
        for issue in issues:
            if issue["id"] in done:
                continue
            if limit is not None and new >= limit:
                break
            pred = predict(issue["title"], issue.get("body", ""))
            f.write(json.dumps({"id": issue["id"], "created_at": issue["created_at"],
                                "predicted": pred, "human_labels": issue["human_labels"]}) + "\n")
            f.flush()
            done.add(issue["id"])   # an id repeated later in `issues` must not be predicted (and paid for) twice
            new += 1
    return new


def predictions_to_records(path: str) -> list[Record]:
    """Category = what the agent proposed. Correct = the maintainers also applied that label."""
    recs = []
    seen: set[str] = set()   # duplicate rows would inflate n and make the Wilson bound look tighter than it is
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            if d["id"] in seen:
                continue
            seen.add(d["id"])
            pred = d["predicted"] if d["predicted"] in COARSE else "invalid"
            recs.append(Record(
                id=d["id"],
                ts=datetime.fromisoformat(d["created_at"].replace("Z", "+00:00")),
                category=f"label:{pred}",
                correct=pred in d["human_labels"],
            ))
    return recs


def _get_predictor(name: str) -> Predictor:
    if name == "baseline":
        from .baseline import predict
        return predict
    if name == "llm":
        from .llm_classifier import make_predictor
        return make_predictor()
    raise SystemExit(f"unknown predictor: {name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("issues")
    ap.add_argument("--predictor", choices=["baseline", "llm"], default="baseline")
    ap.add_argument("--out", required=True, help="predictions JSONL (resumable)")
    ap.add_argument("--records", required=True, help="records JSONL for `python -m rung.cli`")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    new = run_shadow(load_issues(args.issues), _get_predictor(args.predictor), args.out, args.limit)
    recs = predictions_to_records(args.out)
    save_records(args.records, recs)
    print(f"{new} new predictions; {len(recs)} total records -> {args.records}")


if __name__ == "__main__":
    main()
