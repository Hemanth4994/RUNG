# Rung: earned autonomy for AI agents

**Question:** for which kinds of actions has an AI agent earned the right to act without a human, and how sure are we?

Teams usually answer this by gut feel: review everything, or trust everything. Rung answers it with evidence.
It shadow-runs an agent next to real human decisions, measures agreement per action category, and promotes a
category to `auto` only when a *conservative upper bound* on its error rate is low enough, then checks that
decision with a time-ordered backtest.

First benchmark: triaging GitHub issues (does the agent's proposed label match what maintainers applied?).

## How it works (v0)
1. `rung.collect` pulls issues + maintainer-applied labels (the human decision) from public repos.
2. A triage agent (LangGraph) proposes a label per issue. Each outcome becomes a `Record`.
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

## Pipeline commands
```bash
python -m rung.collect owner/repo --max-issues 500 --out data/issues.jsonl      # needs GITHUB_TOKEN
python -m rung.shadow data/issues.jsonl --predictor baseline \
    --out data/pred_baseline.jsonl --records data/records_baseline.jsonl        # no API key needed
python -m rung.cli data/records_baseline.jsonl                                  # evidence + backtest report
# LLM agent (needs provider key): pip install -e ".[agent]" ; export RUNG_MODEL="<provider>:<model>"
python -m rung.shadow data/issues.jsonl --predictor llm \
    --out data/pred_llm.jsonl --records data/records_llm.jsonl
```

## Status
- Tested (23 unit tests): stats, policy, backtest, taxonomy, keyword baseline, shadow runner, gate logic, report CLI, and the agent graph (with a fake classifier).
- Run end to end: the collector (live GitHub), the LLM classifier (Gemini Flash-Lite), and the LangGraph agent with human approval and LangSmith tracing.
- Not built yet: LangSmith dataset and experiments, report page, deployment.

## Honest limitations
- Maintainer labels are noisy ground truth, not perfect truth.
- Synthetic data only checks the code, never counts as a result.
- GitHub triage is a proxy benchmark for the broader agent-autonomy problem.

## Results (v0)

**Setup.** Issues from four public repos (pytest, flask, pandas, scikit-learn), about 1,680 after removing rows that were collected twice. The "human decision" is the label the maintainers applied, mapped to four categories: bug, feature, question, docs. A predictor proposes one label per issue; an error means it disagreed with the maintainers. The policy promotes a category to `auto` only if it has at least 30 cases and the one-sided 95% Wilson upper bound on its error rate is at most the limit (here 5%).

Two predictors were compared:

- **Keyword baseline**: a plain keyword classifier, no API key.
- **LLM**: Gemini Flash-Lite (`gemini-flash-lite-latest`, temperature 0, structured output), run 18-21 Oct 2026.

### LLM, per category (all issues, 5% limit)

| Category | Cases | Errors | Error | Upper bound | Tier |
|---|---|---|---|---|---|
| docs | 398 | 7 | 1.8% | 3.2% | **auto** |
| bug | 941 | 68 | 7.2% | 8.7% | review |
| feature | 318 | 34 | 10.7% | 13.9% | review |
| question | 22 | 12 | 54.5% | 70.5% | review |

### Backtest

The policy is decided on the earliest 60% of issues (by timestamp) and scored on the latest 40%.

- At a 5% limit, `docs` is promoted. On the later issues it handles **19.5% of cases automatically at 2.3% realized error**, with no false promotions.
- An expanding-window check (4 folds) found no fold with a false promotion.

### Coverage versus risk

Share of later issues handled automatically, and the error rate on those issues:

| Error limit | Keyword baseline | LLM |
|---|---|---|
| 2% | 0.0% coverage | 0.0% coverage |
| 5% | 0.0% coverage | 19.5% coverage, 2.3% error |
| 10% | 0.0% coverage | 19.5% coverage, 2.3% error |
| 15% | 0.0% coverage | 82.1% coverage, 4.2% error |

The keyword baseline never earned autonomy in any category at any limit up to 15%. The LLM earned it for one category at 5% and for three at 15%. Realized error stays below the limit in every row because the policy decides on an upper bound, not on the observed rate. Full reports are in `results/`.

### Limitations

- **Ground truth is noisy.** Maintainer labels follow each repo's own conventions, so "error" means disagreement with a maintainer, not objective wrongness.
- **Small counts.** The 19.5% coverage figure rests on roughly 130 later `docs` issues and about 3 errors, so it carries wide uncertainty. `question` has only 22 cases.
- **Narrow data.** Four Python libraries only; results may not transfer to other projects.
- **Model input is limited.** The model sees the title and the first 1,500 characters of the body, and must pick one of four labels even when none fits.
- **Floating model alias.** `gemini-flash-lite-latest` can change over time, so rerunning later may give different numbers.
- **Weak baseline.** A keyword rule is a low bar; a trained text classifier would be a fairer comparison.
- **Dedup mismatch.** Two de-duplication counts differ by 5 rows (1,674 vs 1,679); I haven't traced the cause.

### Agent

The LangGraph agent (`rung.agent`) runs propose, gate, then either apply (auto tier) or pause for a human reply and resume. The graph logic has 7 tests that use a fake classifier. Try it without any API call:

```bash
python -m rung.run_agent data/all_issues.jsonl data/records_llm.jsonl --index 0 --fake bug --reply approve
```

Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to record runs in LangSmith.



![LangSmith traces of one triage run](docs/langsmith-trace.png)


