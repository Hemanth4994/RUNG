"""Rung web page: the real statistics, the real stored results, and the real LangGraph gate, in a browser.

    pip install -e ".[agent,app]"
    streamlit run app/rung_app.py

Nothing here calls a model. The numbers come from results/*.txt (written by the pipeline), and the
gate tab runs the repo's own LangGraph agent with a small stand-in classifier so it works offline.
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from rung.policy import AUTO, PolicyConfig, decide
from rung.stats import CategoryStats, wilson_upper
from rung.taxonomy import COARSE

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FROZEN_LIMIT, FROZEN_MIN_N = 5, 30          # percent, cases (frozen in git tag frozen-v1 before the holdout was scored)

st.set_page_config(page_title="Rung: earned autonomy for AI agents", page_icon="🪜", layout="wide")


# ---------- the stored results (read from the real report files) ----------

def _read(name: str) -> str:
    return (RESULTS / name).read_text(encoding="utf-8-sig")          # the reports start with a byte-order mark


@st.cache_data
def load_dev() -> dict[str, tuple[int, int]]:
    """category -> (cases, errors) on the development repos (pytest, flask, pandas, scikit-learn)."""
    rows = {}
    for line in _read("report_llm.txt").splitlines():
        m = re.match(r"^(label:\w+)\s+(\d+)\s+(\d+)\s+[\d.]+\s+[\d.]+\s+(?:auto|review)\s*$", line)
        if m:
            rows[m[1]] = (int(m[2]), int(m[3]))
    return rows


@st.cache_data
def load_holdout() -> dict[str, tuple[int, int]]:
    """category -> (cases, errors) on the holdout repos (matplotlib, numpy), never used to choose anything."""
    rows = {}
    for line in _read("holdout_llm.txt").splitlines():
        m = re.match(r"^(label:\w+)\s+(?:auto|review)\s+\d+\s+[\d.]+\s+[\d.]+\s+(\d+)\s+(\d+)\s+[\d.]+\s*$", line)
        if m:
            rows[m[1]] = (int(m[2]), int(m[3]))
    return rows


def score(dev, hold, cfg: PolicyConfig) -> dict:
    """Decide from the dev counts only, then score the decision on the holdout counts (same rule as rung.backtest)."""
    stats = {c: CategoryStats(c, n, e, e / n, wilson_upper(e, n, cfg.z)) for c, (n, e) in dev.items()}
    policy = {c: decide(s, cfg) for c, s in stats.items()}
    promoted = [c for c, t in policy.items() if t == AUTO]
    auto_n = sum(hold[c][0] for c in promoted if c in hold)
    auto_err = sum(hold[c][1] for c in promoted if c in hold)
    false_prom = [c for c in promoted if c in hold and hold[c][0] and hold[c][1] / hold[c][0] > cfg.max_error]
    return {"stats": stats, "policy": policy, "promoted": promoted, "auto_n": auto_n, "auto_err": auto_err,
            "false": false_prom}


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


# ---------- sidebar: the policy settings ----------

st.sidebar.header("Policy settings")
limit = st.sidebar.slider("Highest error we accept on auto-handled actions (%)", 1, 20, FROZEN_LIMIT, key="limit")
min_n = st.sidebar.number_input("Fewest cases before a category can be trusted", 1, 200, FROZEN_MIN_N, key="min_n")
if (limit, min_n) == (FROZEN_LIMIT, FROZEN_MIN_N):
    st.sidebar.caption("These are the frozen settings: 5% and 30 cases, fixed in git before the holdout was scored.")
else:
    st.sidebar.warning("You changed the frozen settings. In the real project they were fixed before looking at the "
                       "holdout, because tuning after you look turns the holdout into a second dev set.")
cfg = PolicyConfig(max_error=limit / 100, min_n=int(min_n))

try:
    dev, hold = load_dev(), load_holdout()
    assert dev and hold
except (OSError, AssertionError):
    st.error("Could not read results/report_llm.txt and results/holdout_llm.txt. Run this from a full copy of the repo.")
    st.stop()

res = score(dev, hold, cfg)
hold_total = sum(n for n, _ in hold.values())
hold_wrong_total = sum(e for _, e in hold.values())

# ---------- header ----------

st.title("Rung: earned autonomy for AI agents")
st.markdown("**Question:** for which kinds of actions has an AI agent earned the right to act without a human, "
            "and how sure are we? Rung shadow-runs the agent next to real human decisions, measures its error per "
            "category, and lets a category act alone only when a cautious upper bound on its error is low enough.")

c1, c2, c3 = st.columns(3)
c1.metric("Handled with no human (holdout)", pct(res["auto_n"] / hold_total))
c1.caption(f"{res['auto_n']} of {hold_total} issues")
c2.metric("Error on those", pct(res["auto_err"] / res["auto_n"]) if res["auto_n"] else "-")
c2.caption(f"{res['auto_err']} wrong")
c3.metric("Wrong if the agent acted on everything", pct(hold_wrong_total / hold_total))
c3.caption(f"{hold_wrong_total} wrong of {hold_total}")
st.caption("Holdout: 500 GitHub issues from two repos (matplotlib, numpy) that the policy was never built from. "
           "The numbers above follow the settings in the sidebar.")

tab_idea, tab_evidence, tab_gate = st.tabs(["1. Why a raw error rate is not enough", "2. The evidence", "3. Try the gate"])

# ---------- tab 1: the upper bound ----------

with tab_idea:
    st.markdown("A category that was right 5 times out of 5 has **0% error**, but 5 cases say very little. Rung uses the "
                "upper end of a 95% confidence interval (the Wilson bound) instead: the worst the true error plausibly is.")
    a, b = st.columns(2)
    n = a.number_input("Cases seen in this category", 1, 2000, 34, key="calc_n")
    errors = b.number_input("Of those, wrong", 0, int(n), min(1, int(n)))       # no key: resets cleanly when n changes
    ub = wilson_upper(int(errors), int(n), cfg.z)
    d = decide(CategoryStats("x", int(n), int(errors), errors / n, ub), cfg)
    r1, r2, r3 = st.columns(3)
    r1.metric("Raw error", pct(errors / n))
    r2.metric("Cautious upper bound", pct(ub))
    r3.metric("Decision", "AUTO" if d == AUTO else "REVIEW (human)")
    if d == AUTO:
        st.success(f"{int(n)} cases is at least {cfg.min_n}, and the upper bound {pct(ub)} is within the {limit}% limit.")
    elif n < cfg.min_n:
        st.warning(f"Only {int(n)} cases: fewer than the {cfg.min_n} required, so a human stays in the loop however good it looks.")
    else:
        st.warning(f"The upper bound {pct(ub)} is above the {limit}% limit, so a human stays in the loop.")

    st.markdown("**How the bound shrinks as evidence grows** (same raw error, more cases):")
    ns = list(range(5, 401, 5))
    chart = pd.DataFrame({"cases": ns})
    for p in (0.0, 0.02, 0.05):
        chart[f"{int(p * 100)}% raw error"] = [wilson_upper(p * k, k, cfg.z) * 100 for k in ns]   # fractional errors are fine in the formula
    chart[f"limit ({limit}%)"] = float(limit)
    st.line_chart(chart, x="cases", y_label="upper bound on true error (%)")

# ---------- tab 2: the evidence ----------

with tab_evidence:
    st.markdown("Which categories are `auto` is decided **only** from the development repos. The holdout is only scored. "
                "Move the limit in the sidebar to see why it was frozen first.")
    rows = []
    for c in sorted(dev):
        n_d, e_d = dev[c]
        s = res["stats"][c]
        n_h, e_h = hold.get(c, (0, 0))
        rows.append({
            "Category": c.replace("label:", ""), "Tier": "auto" if res["policy"][c] == AUTO else "review",
            "Dev cases": n_d, "Dev error": pct(s.error_rate), "Dev upper bound": pct(s.upper_bound),
            "Holdout cases": n_h, "Holdout error": pct(e_h / n_h) if n_h else "-",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True)

    if res["false"]:
        names = ", ".join(c.replace("label:", "") for c in res["false"])
        st.error(f"False promotion: **{names}** passed on the dev repos but its holdout error is above the {limit}% limit. "
                 "This is what the frozen 5% limit avoided.")
    elif res["promoted"]:
        st.success("No false promotions: every auto category stayed within the limit on the unseen repos.")
    else:
        st.info("No category earned autonomy at these settings, so everything goes to a human.")

    long = []
    for c in sorted(dev):
        n_h, e_h = hold.get(c, (0, 0))
        long.append({"Category": c.replace("label:", ""), "Measure": "Dev upper bound", "Error %": res["stats"][c].upper_bound * 100})
        if n_h:
            long.append({"Category": c.replace("label:", ""), "Measure": "Holdout error", "Error %": e_h / n_h * 100})
    bars = alt.Chart(pd.DataFrame(long)).mark_bar().encode(
        x=alt.X("Category:N", title=None), xOffset="Measure:N", y=alt.Y("Error %:Q"),
        color=alt.Color("Measure:N", title=None, scale=alt.Scale(range=["#4c78a8", "#e45756"])))
    rule = alt.Chart(pd.DataFrame({"y": [float(limit)]})).mark_rule(strokeDash=[5, 4], color="#888").encode(y=alt.Y("y:Q", title="Error %"))
    st.altair_chart(bars + rule)
    st.caption(f"Dashed line: the {limit}% limit. A category is auto only if its blue bar is under the line and it has "
               f"at least {cfg.min_n} dev cases (question has only {dev.get('label:question', (0, 0))[0]}).")

    with st.expander("Honest limitations"):
        st.markdown("- Maintainer labels are noisy ground truth, not perfect truth.\n"
                    "- GitHub triage is a proxy benchmark for the wider agent-autonomy problem.\n"
                    "- At a 10% limit (a check run after seeing the holdout) `bug` would be promoted and the realized error "
                    "would be 12.9%: that is the peeking problem, and why the settings were frozen in git first.")

# ---------- tab 3: the gate ----------

KEYWORDS = [
    ("docs", ("typo", "docs", "documentation", "readme", "docstring")),
    ("bug", ("crash", "error", "exception", "traceback", "fails", "broken", "bug")),
    ("question", ("how do i", "how to", "why does", "?")),
    ("feature", ("add ", "support for", "feature", "would be nice", "enhancement")),
]


def stand_in_classify(title: str, body: str = "") -> str:
    """A tiny keyword classifier so the page runs offline. In the real runs this role is played by Gemini Flash-Lite."""
    t = title.lower()
    for label, words in KEYWORDS:
        if any(w in t for w in words):
            return label
    return "other"                                           # an unknown label: the gate must fail closed


@st.cache_resource
def get_graph(policy_items: tuple):
    from rung.agent import build_graph
    return build_graph(stand_in_classify, dict(policy_items))


with tab_gate:
    st.markdown("An agent proposes a label for a new issue. The gate checks the policy from the evidence tab. A category "
                "that earned `auto` is applied with **no human**. Everything else **pauses and waits for you** (the real "
                "LangGraph `interrupt` and `Command(resume=...)`, in `src/rung/agent.py`).")
    policy = {c: t for c, t in res["policy"].items()}
    st.markdown("**Current policy:** " + ", ".join(f"`{c.replace('label:', '')}` → **{t}**" for c, t in sorted(policy.items())) +
                ". Any label the policy has never seen fails closed to a human.")
    st.caption("The classifier here is a small keyword stand-in so this page runs offline. The gate logic and the pause and "
               "resume are the real code.")

    try:
        graph = get_graph(tuple(sorted(policy.items())))
    except ImportError:
        st.info('LangGraph is not installed. Run:  pip install -e ".[agent,app]"')
        st.stop()

    ss = st.session_state
    ss.setdefault("history", [])
    ss.setdefault("pending", None)
    sig = tuple(sorted(policy.items()))
    if ss.pending and ss.pending["sig"] != sig:
        ss.pending = None
        st.warning("The policy changed while a run was paused, so that run was dropped.")

    examples = ["Typo in the installation docs", "Crash when calling fit twice", "Error on empty input",
                "Please add a dark theme", "How do I plot two axes?", "Refactor the build system"]
    title = st.text_input("New issue title", examples[0], key="gate_title", disabled=bool(ss.pending))
    st.caption("Try: " + " | ".join(f"“{e}”" for e in examples[1:]))

    def finish(out: dict, thread: str, human: str | None) -> None:
        final = out.get("final_label")
        ss.history.insert(0, {"Issue": out.get("title", ""), "Agent proposed": out.get("proposal"), "Gate": out.get("tier"),
                              "Human said": human or "-", "Applied label": final if final else "none (rejected)"})

    if st.button("Run the agent", key="run", disabled=bool(ss.pending) or not title.strip(), type="primary"):
        thread = uuid.uuid4().hex
        conf = {"configurable": {"thread_id": thread}}
        out = graph.invoke({"issue_id": thread[:8], "title": title.strip(), "body": ""}, conf)
        if "__interrupt__" in out:
            ss.pending = {"thread": thread, "title": title.strip(), "proposal": out["proposal"], "tier": out["tier"], "sig": sig}
        else:
            finish(out, thread, None)
        st.rerun()

    if ss.pending:
        p = ss.pending
        st.warning(f"**Paused for a human.** The agent proposed **{p['proposal']}** for “{p['title']}”, but "
                   f"`label:{p['proposal']}` has not earned autonomy, so nothing is applied until you answer.")
        from langgraph.types import Command
        choices = ["approve"] + list(COARSE) + ["reject"]
        cols = st.columns(len(choices))
        for col, reply in zip(cols, choices):
            if col.button(reply, key=f"reply_{reply}"):
                conf = {"configurable": {"thread_id": p["thread"]}}
                out = graph.invoke(Command(resume=reply), conf)
                finish(out, p["thread"], reply)
                ss.pending = None
                st.rerun()
        st.caption("approve keeps the agent's label. A label replaces it. reject applies nothing.")

    if ss.history:
        st.markdown("**What happened**")
        st.dataframe(pd.DataFrame(ss.history), hide_index=True)
        if st.button("Clear history", key="clear"):
            ss.history = []
            st.rerun()
