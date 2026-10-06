# Rung: earned autonomy for AI agents

**Question:** for which kinds of actions has an AI agent earned the right to act without a human, and how sure are we?

Teams usually answer this by gut feel: review everything, or trust everything. Rung answers it with evidence.
It shadow-runs an agent next to real human decisions, measures agreement per action category, and promotes a
category to `auto` only when a *conservative upper bound* on its error rate is low enough, then checks that
decision with a time-ordered backtest.

First benchmark: triaging GitHub issues (does the agent's proposed label match what maintainers applied?).

## How it works (v0)
1. `rung.collect` pulls issues + maintainer-applied labels (the human decision) from public repos.
2. A triage agent (LangGraph, next step) proposes a label per issue. Each outcome becomes a `Record`.
3. `rung.stats` computes per-category error with a Wilson upper bound.
4. `rung.policy` promotes a category only if n >= min_n **and** upper bound <= max_error.
5. `rung.backtest` decides using only past data and scores on future data. It reports coverage, realized error,
   and **false promotions** (categories trusted on old data that failed on new data).

## Quickstart
```bash
pip install -e .
export PYTHONPATH=src
python -m unittest discover -s tests -v
python scripts/make_synthetic.py            # fake data, only to sanity-check the pipeline
python -m rung.cli data/synthetic.jsonl
```

## Status
- Tested (unit tests + synthetic data): stats, policy, backtest, label taxonomy, report CLI.
- Written but **not yet run against live GitHub**: `rung.collect`.
- Not built yet: the LangGraph triage agent, LangSmith tracing, human-approval interrupt step, report page.

## Honest limitations
- Maintainer labels are noisy ground truth, not perfect truth.
- Synthetic data only checks the code, never counts as a result.
- GitHub triage is a proxy benchmark for the broader agent-autonomy problem.
