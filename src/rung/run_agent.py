"""Run the triage graph on one issue (propose -> gate -> apply, or pause for a human).

Run from the project root with the venv active:

  # no API call: pretend the model proposed "docs" (auto-tier when docs is promoted)
  python -m rung.run_agent data/all_issues.jsonl data/records_llm.jsonl --index 0 --fake docs

  # no API call: "bug" is not promoted, so the graph pauses for a human
  python -m rung.run_agent data/all_issues.jsonl data/records_llm.jsonl --index 0 --fake bug --reply approve

  # real model (needs RUNG_MODEL and the provider's API key set)
  python -m rung.run_agent data/all_issues.jsonl data/records_llm.jsonl --index 3

Set LANGSMITH_TRACING=true and LANGSMITH_API_KEY to record each run in LangSmith.
"""
from __future__ import annotations

import argparse
import json

from langgraph.types import Command

from .agent import build_graph
from .policy import PolicyConfig, build_policy
from .records import Record


def _read_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_records(path: str) -> list[Record]:
    return [
        Record(id=r["id"], ts=r["ts"], category=r["category"], correct=r["correct"])
        for r in _read_jsonl(path)
    ]


def _issue_id(row: dict) -> str:
    return str(row.get("id", row.get("number")))


def pick_issue(rows: list[dict], issue_id: str | None, index: int) -> dict:
    if issue_id is not None:
        for row in rows:
            if _issue_id(row) == str(issue_id):
                return row
        raise SystemExit(f"No issue with id {issue_id}")
    return rows[index]


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("issues", help="issues JSONL (from rung.collect)")
    p.add_argument("records", help="records JSONL used to build the policy (from rung.shadow)")
    p.add_argument("--id", help="issue id to run (default: use --index)")
    p.add_argument("--index", type=int, default=0, help="row number in the issues file")
    p.add_argument("--max-error", type=float, default=0.05)
    p.add_argument("--min-n", type=int, default=30)
    p.add_argument("--fake", choices=["bug", "feature", "question", "docs"],
                   help="skip the model and propose this label (no API call)")
    p.add_argument("--reply", help="human reply if the graph pauses; asked interactively if omitted")
    args = p.parse_args(argv)

    policy = build_policy(load_records(args.records), PolicyConfig(max_error=args.max_error, min_n=args.min_n))
    print("Policy:", policy)

    row = pick_issue(_read_jsonl(args.issues), args.id, args.index)
    issue_id = _issue_id(row)
    title = row.get("title", "")
    body = row.get("body") or ""
    if not title:
        raise SystemExit("This issue row has no 'title' field. Fields found: " + ", ".join(row))
    print(f"Issue {issue_id}: {title[:100]}")

    if args.fake:
        label = args.fake
        classify = lambda title, body: label  # noqa: E731
    else:
        from .llm_classifier import make_predictor

        classify = make_predictor()

    graph = build_graph(classify, policy)
    config = {
        "configurable": {"thread_id": issue_id},
        "run_name": "rung-triage",
        "tags": ["rung"],
        "metadata": {"issue_id": issue_id},
    }

    result = graph.invoke({"issue_id": issue_id, "title": title, "body": body}, config)

    pending = result.get("__interrupt__")
    if pending:
        print("PAUSED for human review:", pending[0].value)
        reply = args.reply or input("Reply (approve / bug / feature / question / docs / reject): ")
        result = graph.invoke(Command(resume=reply), config)

    print(f"proposal={result.get('proposal')}  tier={result.get('tier')}  final_label={result.get('final_label')}")
    print("maintainers applied:", row.get("human_labels"))


if __name__ == "__main__":
    main()
