"""Apply a FROZEN policy to a holdout set.

    python -m rung.holdout DEV_RECORDS HOLDOUT_RECORDS [--max-error 0.05] [--min-n 30]

Which categories are `auto` is decided ONLY from DEV_RECORDS. HOLDOUT_RECORDS (from repos the
development work never touched) is only scored, never used to choose anything. The report shows
coverage and realized error on auto-handled holdout cases, false promotions (promoted on dev but
worse than the limit on the holdout), and every category's dev vs holdout error side by side.

Do not tune settings after looking at this output: that turns the holdout into a second dev set.
"""
from __future__ import annotations

import argparse

from .backtest import BacktestResult, evaluate_split
from .policy import REVIEW, PolicyConfig, build_policy
from .records import Record, load_records
from .stats import category_stats


def run_holdout(dev: list[Record], holdout: list[Record], cfg: PolicyConfig) -> tuple[BacktestResult, list[dict]]:
    policy = build_policy(dev, cfg)
    dev_s, hold_s = category_stats(dev, cfg.z), category_stats(holdout, cfg.z)
    rows = []
    for cat in sorted(set(dev_s) | set(hold_s)):
        d, h = dev_s.get(cat), hold_s.get(cat)
        rows.append({
            "category": cat, "tier": policy.get(cat, REVIEW),
            "dev_n": d.n if d else 0, "dev_err": d.error_rate if d else None,
            "dev_upper": d.upper_bound if d else None,
            "hold_n": h.n if h else 0, "hold_errors": h.errors if h else 0,
            "hold_err": h.error_rate if h else None,
        })
    return evaluate_split(dev, holdout, cfg), rows


def _pct(v: float | None) -> str:
    return "-" if v is None else f"{v * 100:.1f}"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="rung.holdout")
    ap.add_argument("dev_records")
    ap.add_argument("holdout_records")
    ap.add_argument("--max-error", type=float, default=0.05)
    ap.add_argument("--min-n", type=int, default=30)
    a = ap.parse_args(argv)
    cfg = PolicyConfig(max_error=a.max_error, min_n=a.min_n)
    res, rows = run_holdout(load_records(a.dev_records), load_records(a.holdout_records), cfg)

    print(f"policy from {res.n_train} dev records (error <= {cfg.max_error:.0%}, min n = {cfg.min_n}); "
          f"scored on {res.n_test} holdout records")
    print(f"{'category':<18}{'tier':<8}{'dev n':>7}{'dev err%':>10}{'dev upper%':>12}"
          f"{'hold n':>8}{'hold err':>9}{'hold err%':>10}")
    for r in rows:
        print(f"{r['category']:<18}{r['tier']:<8}{r['dev_n']:>7}{_pct(r['dev_err']):>10}{_pct(r['dev_upper']):>12}"
              f"{r['hold_n']:>8}{r['hold_errors']:>9}{_pct(r['hold_err']):>10}")
    print(f"\npromoted: {res.promoted or 'none'}")
    print(f"holdout coverage: {res.coverage:.1%} ({res.auto_n} of {res.n_test}), "
          f"realized error on auto-handled: {res.auto_error_rate:.1%} ({res.auto_errors} wrong)")
    print(f"false promotions: {res.false_promotions or 'none'}")


if __name__ == "__main__":
    main()
