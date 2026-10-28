"""A TRAINED baseline (TF-IDF + logistic regression) that is leakage-free by construction.

    python -m rung.baseline_ml data/issues.jsonl \
        --out data/pred_ml.jsonl --records data/records_ml.jsonl [--blocks 10]

Why walk-forward: Rung backtests a predictor on time-ordered records. A model trained on
the whole dataset and then scored on it would have seen the very issues it is graded on, and
a model trained on later issues would "know the future". Either contaminates the backtest.

Design
------
1. Drop repeated ids (first occurrence wins), sort by created_at (stable), and cut the
   sequence into ``n_blocks`` contiguous blocks of near-equal size (fewer blocks if there are
   fewer issues; never an empty block).
2. Only issues with EXACTLY ONE (distinct) human label, that label being in COARSE, are
   "trainable". Issues with 0 or 2+ labels still get a prediction but are never training rows.
3. Block 0 has no earlier data, so it is predicted by K-fold cross-validation inside block 0
   only: each fold is predicted by a model fit on the trainable issues of the other folds.
   StratifiedKFold is used when every class present has >= n_folds trainable rows, otherwise
   a shuffled KFold seeded with ``seed``. Issues that are not trainable are spread over the
   folds round-robin so they are predicted too.
4. Block k >= 1 is predicted by one model fit on the trainable issues of blocks 0..k-1 only.
5. Model: TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=50000)
   -> LogisticRegression(max_iter=1000, random_state=seed), no class_weight. Text is
   ``title + "\\n" + body[:1500]`` (the same truncation the LLM predictor uses).

Fallbacks (all documented, none silent in the trace)
----------------------------------------------------
* no trainable rows           -> predict "bug" (the keyword baseline's default as well);
* only one class in training  -> predict that class;
* min_df=2 leaves no vocabulary -> retry with min_df=1;
* still no vocabulary         -> predict the majority training class (ties: COARSE order).

LEAKAGE GUARANTEE
-----------------
Every prediction for an issue comes from a model that never saw that issue. For issues after
block 0 the model was trained only on strictly earlier blocks, so every training row has
created_at <= every row being predicted (equal only for timestamp ties across a block
boundary). Block 0 has no earlier data, so it is cross-validated inside itself: a fold may be
trained on block-0 issues that are later than the ones it predicts, but never on any issue
from a later block. Block 0 is therefore the only part of the output that is cross-validated
rather than strictly walk-forward. ``trace`` records exactly which ids went into and came out
of every fit so tests (and reviewers) can verify all of this.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, StratifiedKFold

from .records import save_records
from .shadow import load_issues, predictions_to_records
from .taxonomy import COARSE

FALLBACK_LABEL = "bug"   # used only when there is no trainable row at all
BODY_CHARS = 1500        # same truncation as llm_classifier


def _ts(created_at: str) -> datetime:
    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _text(issue: dict) -> str:
    return f"{issue.get('title') or ''}\n{(issue.get('body') or '')[:BODY_CHARS]}"


def _single_label(issue: dict) -> str | None:
    """The issue's training label, or None if it is not a trainable row."""
    labels = set(issue.get("human_labels") or [])
    if len(labels) != 1:
        return None
    (label,) = labels
    return label if label in COARSE else None


def _majority(labels: Sequence[str]) -> str:
    return max(COARSE, key=lambda c: (labels.count(c), -COARSE.index(c)))


def _fit_predict(train_texts: list[str], train_labels: list[str], test_texts: list[str],
                 seed: int) -> list[str]:
    if not test_texts:
        return []
    if not train_labels:
        return [FALLBACK_LABEL] * len(test_texts)
    if len(set(train_labels)) < 2:
        return [train_labels[0]] * len(test_texts)

    def vectorizer(min_df: int) -> TfidfVectorizer:
        return TfidfVectorizer(ngram_range=(1, 2), min_df=min_df, sublinear_tf=True,
                               max_features=50000)

    vec = vectorizer(2)
    try:
        x_train = vec.fit_transform(train_texts)
    except ValueError:                       # min_df=2 pruned the whole (tiny) vocabulary
        vec = vectorizer(1)
        try:
            x_train = vec.fit_transform(train_texts)
        except ValueError:                   # no usable tokens at all
            return [_majority(train_labels)] * len(test_texts)
    clf = LogisticRegression(max_iter=1000, random_state=seed)
    clf.fit(x_train, train_labels)
    return [str(p) for p in clf.predict(vec.transform(test_texts))]


def _block_bounds(n: int, n_blocks: int) -> list[tuple[int, int]]:
    b = max(1, min(n_blocks, n))
    base, extra = divmod(n, b)
    bounds, start = [], 0
    for i in range(b):
        size = base + (1 if i < extra else 0)
        bounds.append((start, start + size))
        start += size
    return bounds


def _cv_folds(labels: list[str | None], n_folds: int, seed: int) -> list[list[int]]:
    """Partition block-0 positions into test folds (lists of positions, ascending)."""
    n = len(labels)
    trainable = [i for i, lab in enumerate(labels) if lab is not None]
    others = [i for i, lab in enumerate(labels) if lab is None]
    y = [labels[i] for i in trainable]
    if trainable and min(y.count(c) for c in set(y)) >= n_folds:
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
        folds = [[trainable[j] for j in test] for _, test in skf.split(trainable, y)]
        for r, i in enumerate(others):       # round-robin so non-trainable issues get predicted
            folds[r % n_folds].append(i)
        return [sorted(f) for f in folds]
    k = min(n_folds, n)
    if k < 2:
        return [list(range(n))]              # one issue: nothing to train on
    kf = KFold(n_splits=k, shuffle=True, random_state=seed)
    return [sorted(int(i) for i in test) for _, test in kf.split(list(range(n)))]


def walk_forward_predictions(issues: list[dict], n_blocks: int = 10, n_folds: int = 5,
                             seed: int = 0, trace: list | None = None) -> list[dict]:
    """Leakage-free predictions for every unique issue, in time order. See module docstring.

    If ``trace`` is a list, one dict per fit is appended:
    {"block": k, "mode": "cv" | "forward", "train_ids": [...], "predict_ids": [...]}.
    A fit that is skipped because of a fallback (no/one training class) is still traced.
    """
    n_folds = max(2, n_folds)
    seen: set[str] = set()
    unique: list[dict] = []
    for issue in issues:
        if issue["id"] not in seen:
            seen.add(issue["id"])
            unique.append(issue)
    unique.sort(key=lambda d: _ts(d["created_at"]))          # stable
    if not unique:
        return []

    texts = [_text(d) for d in unique]
    labels = [_single_label(d) for d in unique]
    ids = [d["id"] for d in unique]
    predicted: list[str] = [FALLBACK_LABEL] * len(unique)
    bounds = _block_bounds(len(unique), n_blocks)

    def note(block: int, mode: str, train: list[int], test: list[int]) -> None:
        if trace is not None:
            trace.append({"block": block, "mode": mode,
                          "train_ids": [ids[i] for i in train],
                          "predict_ids": [ids[i] for i in test]})

    # Block 0: cross-validation inside the block only.
    lo, hi = bounds[0]
    for fold in _cv_folds(labels[lo:hi], n_folds, seed):
        test = [lo + i for i in fold]
        held = set(test)
        train = [i for i in range(lo, hi) if i not in held and labels[i] is not None]
        preds = _fit_predict([texts[i] for i in train], [labels[i] for i in train],
                             [texts[i] for i in test], seed)
        for i, p in zip(test, preds):
            predicted[i] = p
        note(0, "cv", train, test)

    # Blocks 1..: fit on trainable issues of all earlier blocks only.
    for k in range(1, len(bounds)):
        lo, hi = bounds[k]
        train = [i for i in range(bounds[0][0], lo) if labels[i] is not None]
        test = list(range(lo, hi))
        preds = _fit_predict([texts[i] for i in train], [labels[i] for i in train],
                             [texts[i] for i in test], seed)
        for i, p in zip(test, preds):
            predicted[i] = p
        note(k, "forward", train, test)

    return [{"id": d["id"], "created_at": d["created_at"], "predicted": predicted[i],
             "human_labels": list(d.get("human_labels") or [])}
            for i, d in enumerate(unique)]


def run(issues_path: str, out_path: str, records_path: str, n_blocks: int = 10,
        n_folds: int = 5, seed: int = 0) -> int:
    """Load issues, write predictions (overwrite) and records. Returns number of predictions."""
    rows = walk_forward_predictions(load_issues(issues_path), n_blocks=n_blocks,
                                    n_folds=n_folds, seed=seed)
    for path in (out_path, records_path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    save_records(records_path, predictions_to_records(out_path))
    return len(rows)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Walk-forward TF-IDF + logistic regression baseline")
    ap.add_argument("issues")
    ap.add_argument("--out", required=True, help="predictions JSONL (overwritten)")
    ap.add_argument("--records", required=True, help="records JSONL for `python -m rung.cli`")
    ap.add_argument("--blocks", type=int, default=10)
    args = ap.parse_args(argv)
    n = run(args.issues, args.out, args.records, n_blocks=args.blocks)
    print(f"{n} predictions -> {args.out}, {args.records}")


if __name__ == "__main__":
    main()
