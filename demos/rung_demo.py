"""Rung demo: the real statistics and policy code, the real stored reports, and the real LangGraph agent with a stand-in classifier.

From the root of the RUNG folder (needs: pip install -e ".[agent]"):
    python demos/rung_demo.py                       # or: python demos/rung_demo.py path/to/results
"""
import sys
from pathlib import Path

from langgraph.types import Command

from rung.agent import build_graph
from rung.policy import PolicyConfig, decide
from rung.stats import CategoryStats, wilson_upper

sys.stdout.reconfigure(encoding="utf-8")
RESULTS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "results"
cfg = PolicyConfig()                                   # frozen settings: error limit 5%, at least 30 cases, one-sided 95%


def show(title):
    print("\n" + "=" * 8, title, "=" * 8)


show("1. Why a raw error rate is not enough: the cautious upper bound (rung.stats.wilson_upper)")
print(f"{'cases':>6} {'errors':>7} {'raw error':>10} {'upper bound':>12}   decision (limit 5%, at least 30 cases)")
for n, errs in [(5, 0), (30, 0), (34, 1), (103, 3), (100, 7), (400, 8)]:
    ub = wilson_upper(errs, n)
    d = decide(CategoryStats("x", n, errs, errs / n, ub), cfg)
    print(f"{n:>6} {errs:>7} {errs / n:>9.1%} {ub:>12.1%}   {d}")
print("\nFive correct in a row looks perfect (0% error) but the true error could be 35%, so it never earns autonomy.")

show("2. Real report on the development repos (pytest, flask, pandas, scikit-learn), Gemini Flash-Lite")
print((RESULTS / "report_llm.txt").read_text(encoding="utf-8-sig")[:2600])

show("3. Real report on the frozen holdout (matplotlib, numpy), policy decided before these repos were collected")
print((RESULTS / "holdout_llm.txt").read_text(encoding="utf-8-sig")[:2600])

show("4. The runtime gate: the LangGraph agent (a stand-in classifier replaces Gemini here, so it runs offline)")
policy = {"label:docs": "auto", "label:bug": "review", "label:feature": "review", "label:question": "review"}
print("policy from evidence:", policy)


def classify(title, body):
    t = title.lower()
    return "docs" if ("typo" in t or "docs" in t) else "bug" if ("crash" in t or "error" in t) else "wontfix"


graph = build_graph(classify, policy)


def run(issue_id, title, human=None):
    cfg_ = {"configurable": {"thread_id": issue_id}}
    out = graph.invoke({"issue_id": issue_id, "title": title, "body": ""}, cfg_)
    print(f"\n#{issue_id} {title!r}\n  agent proposes: {out.get('proposal')}   gate: {out.get('tier')}")
    if "__interrupt__" in out:
        print("  PAUSED for a human:", out["__interrupt__"][0].value)
        if human is not None:
            print(f"  human replies: {human!r}")
            out = graph.invoke(Command(resume=human), cfg_)
    print("  final label applied:", out.get("final_label"))


run("1", "Typo in the installation docs")                    # docs earned autonomy: applied with no human
run("2", "Crash when calling fit twice", human="approve")    # bug is still in review: pauses, human approves
run("3", "Error on empty input", human="docs")               # human overrides the proposal
run("4", "Please add a dark theme", human="reject")          # unknown category fails closed to a human, who rejects
