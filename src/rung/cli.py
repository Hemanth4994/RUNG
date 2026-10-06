from __future__ import annotations

import argparse

from .backtest import coverage_risk_curve, expanding_window, temporal_backtest
from .policy import PolicyConfig, build_policy
from .records import load_records
from .stats import category_stats


def main() -> None:
    ap = argparse.ArgumentParser(prog="rung")
    ap.add_argument("records", help="JSONL of {id, ts, category, correct}")
    ap.add_argument("--max-error", type=float, default=0.05)
    ap.add_argument("--min-n", type=int, default=30)
    args = ap.parse_args()

    recs = load_records(args.records)
    cfg = PolicyConfig(max_error=args.max_error, min_n=args.min_n)
    stats = category_stats(recs, cfg.z)
    policy = build_policy(recs, cfg)

    print(f"{len(recs)} observations, bound: error <= {cfg.max_error:.0%}, min n = {cfg.min_n}\n")
    print(f"{'category':<20}{'n':>6}{'errors':>8}{'err%':>8}{'upper%':>9}  tier")
    for c, s in sorted(stats.items()):
        print(f"{c:<20}{s.n:>6}{s.errors:>8}{s.error_rate*100:>8.1f}{s.upper_bound*100:>9.1f}  {policy[c]}")

    bt = temporal_backtest(recs, cfg)
    print(f"\nTemporal backtest (60/40): promoted={bt.promoted}")
    print(f"  coverage={bt.coverage:.1%}  realized auto error={bt.auto_error_rate:.1%}  "
          f"false promotions={bt.false_promotions or 'none'}")

    folds = expanding_window(recs, cfg)
    fp = sum(1 for f in folds if f.false_promotions)
    print(f"\nExpanding-window folds: {len(folds)}; folds with a false promotion: {fp}")

    print("\nCoverage vs. risk (max_error -> coverage, realized error):")
    for me, cov, err in coverage_risk_curve(recs, [0.02, 0.05, 0.10, 0.15], args.min_n):
        print(f"  {me:>5.0%} -> {cov:>6.1%}, {err:>6.1%}")


if __name__ == "__main__":
    main()
