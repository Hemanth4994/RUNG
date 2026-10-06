"""Honest evaluation: decide using only the past, then score on the future."""
from __future__ import annotations

from dataclasses import dataclass, field

from .policy import AUTO, PolicyConfig, build_policy
from .records import Record


@dataclass
class BacktestResult:
    n_train: int
    n_test: int
    promoted: list[str]
    auto_n: int                 # test actions that fell in promoted categories
    auto_errors: int
    coverage: float             # auto_n / n_test
    auto_error_rate: float      # realized error on auto-handled test actions
    false_promotions: list[str] = field(default_factory=list)  # promoted, but test error > max_error


def _sorted(records: list[Record]) -> list[Record]:
    return sorted(records, key=lambda r: r.ts)


def evaluate_split(train: list[Record], test: list[Record], cfg: PolicyConfig) -> BacktestResult:
    policy = build_policy(train, cfg)
    promoted = sorted(c for c, t in policy.items() if t == AUTO)
    per_cat: dict[str, list[int]] = {c: [0, 0] for c in promoted}  # [n, errors] on test
    for r in test:
        if r.category in per_cat:
            per_cat[r.category][0] += 1
            per_cat[r.category][1] += 0 if r.correct else 1
    auto_n = sum(v[0] for v in per_cat.values())
    auto_err = sum(v[1] for v in per_cat.values())
    false_prom = [c for c, (n, e) in per_cat.items() if n > 0 and e / n > cfg.max_error]
    return BacktestResult(
        n_train=len(train), n_test=len(test), promoted=promoted,
        auto_n=auto_n, auto_errors=auto_err,
        coverage=auto_n / len(test) if test else 0.0,
        auto_error_rate=auto_err / auto_n if auto_n else 0.0,
        false_promotions=sorted(false_prom),
    )


def temporal_backtest(records: list[Record], cfg: PolicyConfig, train_frac: float = 0.6) -> BacktestResult:
    recs = _sorted(records)
    cut = int(len(recs) * train_frac)
    return evaluate_split(recs[:cut], recs[cut:], cfg)


def expanding_window(records: list[Record], cfg: PolicyConfig,
                     n_folds: int = 4, start_frac: float = 0.4) -> list[BacktestResult]:
    """Train on everything before each fold, test on that fold. More stable than one split."""
    recs = _sorted(records)
    n = len(recs)
    start = int(n * start_frac)
    fold = max(1, (n - start) // n_folds)
    results = []
    for i in range(n_folds):
        lo = start + i * fold
        hi = n if i == n_folds - 1 else lo + fold
        if lo >= n:
            break
        results.append(evaluate_split(recs[:lo], recs[lo:hi], cfg))
    return results


def coverage_risk_curve(records: list[Record], max_errors: list[float], min_n: int = 30,
                        train_frac: float = 0.6) -> list[tuple[float, float, float]]:
    """(max_error, coverage, realized_error) for each bound: the core tradeoff chart."""
    out = []
    for me in max_errors:
        res = temporal_backtest(records, PolicyConfig(max_error=me, min_n=min_n), train_frac)
        out.append((me, res.coverage, res.auto_error_rate))
    return out
