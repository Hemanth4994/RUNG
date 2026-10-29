"""List every wrong prediction of a run, ready for hand tagging. Plain Python, no extra packages.

    python scripts/failures.py data/holdout_issues.jsonl data/hold_pred_llm.jsonl --out results/holdout_llm_failures.md

A prediction is wrong when the maintainers did not apply that label (the same rule the scorer uses).
Read each one and fill in a tag:  ambiguous label | maintainer inconsistency | real miss.
This is for describing the errors honestly in the README. It is NOT for tuning the predictor on the holdout.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter


def read(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def wrong_predictions(issues: list[dict], preds: list[dict]) -> list[dict]:
    """Issues whose prediction is not among the maintainers' labels. One row per issue id."""
    by_id = {i["id"]: i for i in issues}
    seen: set[str] = set()
    out = []
    for p in preds:
        if p["id"] in seen or p["id"] not in by_id:
            continue
        seen.add(p["id"])
        if p["predicted"] not in p["human_labels"]:
            out.append({**by_id[p["id"]], "predicted": p["predicted"]})
    return out


def _url(issue: dict) -> str:
    repo, _, num = issue["id"].partition("#")
    return f"https://github.com/{repo}/issues/{num}"


def _excerpt(text: str, n: int = 300) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= n else text[:n].rstrip() + " ..."


def render(wrong: list[dict], total: int) -> str:
    pairs = Counter((w["predicted"], "+".join(sorted(w["human_labels"])) or "(none)") for w in wrong)
    lines = [f"# Wrong predictions: {len(wrong)} of {total}", "",
             "Tag each: `ambiguous label` | `maintainer inconsistency` | `real miss`", "",
             "## Predicted vs maintainers' label(s)", "", "| predicted | maintainers | count |", "|---|---|---|"]
    lines += [f"| {p} | {h} | {c} |" for (p, h), c in pairs.most_common()]
    lines += ["", "## Cases", ""]
    for n, w in enumerate(sorted(wrong, key=lambda x: (x["predicted"], x["id"])), 1):
        lines += [f"### {n}. {w['id']}  predicted **{w['predicted']}**, maintainers {w['human_labels']}",
                  _url(w), f"Title: {w['title']}", f"Body: {_excerpt(w.get('body', ''))}", "Tag: ", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("issues")
    ap.add_argument("predictions")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    issues, preds = read(a.issues), read(a.predictions)
    wrong = wrong_predictions(issues, preds)
    total = len({p["id"] for p in preds})
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(render(wrong, total))
    print(f"{len(wrong)} wrong of {total} -> {a.out}")


if __name__ == "__main__":
    main()
