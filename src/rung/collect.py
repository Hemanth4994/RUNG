"""Collect GitHub issues + the labels maintainers actually applied (our 'human decision').

Usage:
    export GITHUB_TOKEN=...   # optional but strongly recommended (rate limits)
    python -m rung.collect owner/repo --max-issues 500 --out data/issues.jsonl

NOTE: written against the public GitHub REST API; not yet run against live data.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import requests

from .taxonomy import coarse_labels

API = "https://api.github.com"


def fetch_issues(repo: str, max_issues: int, token: str | None = None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    page, got = 1, 0
    while got < max_issues:
        resp = requests.get(f"{API}/repos/{repo}/issues", headers=headers, timeout=30,
                            params={"state": "all", "per_page": 100, "page": page,
                                    "sort": "created", "direction": "desc"})
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            time.sleep(max(1, reset - int(time.time())) + 1)
            continue
        resp.raise_for_status()
        items = resp.json()
        if not items:
            return
        for it in items:
            if "pull_request" in it:      # the issues endpoint also returns PRs
                continue
            labels = [l["name"] for l in it.get("labels", [])]
            truth = sorted(coarse_labels(labels))
            if not truth:                 # no usable human decision -> not an observation
                continue
            yield {"id": f"{repo}#{it['number']}", "repo": repo, "created_at": it["created_at"],
                   "title": it["title"], "body": (it.get("body") or "")[:2000],
                   "raw_labels": labels, "human_labels": truth}
            got += 1
            if got >= max_issues:
                return
        page += 1


def existing_ids(path: str) -> set[str]:
    """Ids already saved in `path` (empty set if the file does not exist yet)."""
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {json.loads(line)["id"] for line in f if line.strip()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--max-issues", type=int, default=500)
    ap.add_argument("--out", default="data/issues.jsonl")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    seen = existing_ids(args.out)   # re-running the collector must not append the same issue twice
    with open(args.out, "a", encoding="utf-8") as f:
        n = skipped = 0
        for row in fetch_issues(args.repo, args.max_issues, os.environ.get("GITHUB_TOKEN")):
            if row["id"] in seen:
                skipped += 1
                continue
            seen.add(row["id"])
            f.write(json.dumps(row) + "\n")
            n += 1
    print(f"wrote {n} new issues from {args.repo} to {args.out} ({skipped} already present)")


if __name__ == "__main__":
    main()
