# Additions for the Rung README (paste under "Pipeline commands")

## Frozen settings (set BEFORE the holdout run)
- Error limit 5% on the one-sided 95% Wilson upper bound (z = 1.645), `min_n` = 30.
- Time split 60/40 by timestamp, plus a 4-fold expanding window.
- These were fixed before any holdout repo was collected. Commit and tag them (`git tag frozen-v1`).
  If a setting changes later, say so here and do not call the later run a holdout.

## Stronger baseline: trained text classifier
```bash
pip install scikit-learn duckdb          # or add them to pyproject extras (see below)
python -m rung.baseline_ml data/all_issues.jsonl \
    --out data/pred_ml.jsonl --records data/records_ml.jsonl
python -m rung.cli data/records_ml.jsonl
```
TF-IDF (1-2 grams) + logistic regression, trained **walk-forward**: issues are sorted by time and cut into
10 blocks; block k is predicted by a model fit only on blocks 0..k-1. No prediction comes from a model that saw
that issue or any later issue. Block 0 has no past, so it is cross-validated inside itself, which is the only part
of the output that is not strictly walk-forward. Only issues with exactly one maintainer label are used for
training. The LLM predictor and this baseline are therefore compared under the same time-ordered rules.

## SQL layer (DuckDB)
```bash
python -m rung.sqlstats stats    data/records_llm.jsonl
python -m rung.sqlstats backtest data/records_llm.jsonl --max-error 0.05 --min-n 30
python -m rung.sqlstats compare  keyword=data/records_baseline.jsonl ml=data/records_ml.jsonl llm=data/records_llm.jsonl
python -m rung.sqlstats quality  data/all_issues.jsonl --preds keyword=data/pred_baseline.jsonl llm=data/pred_llm.jsonl
```
The same statistics and backtest are written in SQL, and `tests/test_sqlstats.py` checks they equal the Python
results (including heavily tied timestamps and the float edge in the 60% cut). `compare` restricts every
predictor to the issue ids they all share, so a few extra rows in one run cannot skew the comparison.
`quality` reports duplicates, missing fields, per-repo counts and which ids are missing from each prediction file.

## Holdout protocol
1. Tag the frozen settings.
2. Collect 2 repos not used before (about 500 issues in total).
3. Run each predictor once with the frozen settings. Do not tune anything afterwards.
4. Report the holdout table next to the development results, including failures.
5. Read 20-30 wrong predictions by hand and tag each: ambiguous label, maintainer inconsistency, or real miss.

## Update to the Limitations list
- Replace the "Weak baseline" bullet with: "A trained TF-IDF + logistic-regression baseline (walk-forward,
  leakage-free) is included; its results are reported next to the keyword and LLM predictors."
- Keep the dedup bullet until `sqlstats compare` on the two records files explains the 1,674 vs 1,679 gap.

## pyproject.toml (one line under [project.optional-dependencies])
```toml
analysis = ["scikit-learn>=1.3", "duckdb>=1.0"]
```
