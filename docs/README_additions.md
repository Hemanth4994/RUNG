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

## Holdout protocol (PowerShell)
Development files (already made): `data/all_issues.jsonl` and the dev records of each predictor
(`data/records_baseline.jsonl`, `data/records_ml.jsonl`, `data/records_llm.jsonl`; use your own names).
The policy is decided from the dev records only. Holdout repos are scored once and never used to choose anything.

```powershell
# 1. freeze the settings first
git tag frozen-v1 ; git push origin frozen-v1

# 2. collect 2 NEW repos into a SEPARATE file (about 250 issues each). Collect each repo once.
python -m rung.collect OWNER/REPO1 --max-issues 250 --out data/holdout_issues.jsonl
python -m rung.collect OWNER/REPO2 --max-issues 250 --out data/holdout_issues.jsonl

# 3. each predictor runs once on the holdout
python -m rung.shadow data/holdout_issues.jsonl --predictor baseline --out data/hold_pred_kw.jsonl --records data/hold_rec_kw.jsonl
python -m rung.baseline_ml data/holdout_issues.jsonl --train-on data/all_issues.jsonl --out data/hold_pred_ml.jsonl --records data/hold_rec_ml.jsonl
python -m rung.shadow data/holdout_issues.jsonl --predictor llm --out data/hold_pred_llm.jsonl --records data/hold_rec_llm.jsonl

# 4. apply the frozen dev policy to each holdout
python -m rung.holdout data/records_baseline.jsonl data/hold_rec_kw.jsonl
python -m rung.holdout data/records_ml.jsonl data/hold_rec_ml.jsonl
python -m rung.holdout data/records_llm.jsonl data/hold_rec_llm.jsonl
```
Notes
- Pick holdout repos whose labels map to bug / feature / question / docs. Check the collector's "wrote N issues" line.
- `--train-on` fits the trained baseline once on the dev issues and predicts repos it has never seen.
- The free Gemini tier allows about 500 requests a day. Use `--limit` and rerun the same command next day: runs resume.
- `gemini-flash-lite-latest` is a floating alias; write down the date of the holdout run.
- Save each report to `results/` and commit it, including bad results.
- Read 20-30 wrong holdout predictions by hand and tag each: ambiguous label, maintainer inconsistency, or real miss.

## Update to the Limitations list
- Replace the "Weak baseline" bullet with: "A trained TF-IDF + logistic-regression baseline (walk-forward,
  leakage-free) is included; its results are reported next to the keyword and LLM predictors."
- Keep the dedup bullet until `sqlstats compare` on the two records files explains the 1,674 vs 1,679 gap.

## pyproject.toml (one line under [project.optional-dependencies])
```toml
analysis = ["scikit-learn>=1.3", "duckdb>=1.0"]
```
