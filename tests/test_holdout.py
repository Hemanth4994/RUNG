import contextlib
import io
import os
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from rung.holdout import main, run_holdout
from rung.policy import PolicyConfig
from rung.records import Record, save_records

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def recs(cat, n, n_errors, start=0, prefix="x"):
    return [Record(f"{prefix}{cat}{start + i}", T0 + timedelta(hours=start + i), cat, i >= n_errors)
            for i in range(n)]


CFG = PolicyConfig(max_error=0.05, min_n=30)


class TestHoldout(unittest.TestCase):
    def test_policy_comes_from_dev_only_and_degradation_is_flagged(self):
        dev = recs("label:a", 400, 4) + recs("label:b", 100, 40, prefix="d")   # a reliable, b not
        hold = recs("label:a", 100, 15, prefix="h") + recs("label:b", 50, 0, prefix="h")
        res, rows = run_holdout(dev, hold, CFG)
        self.assertEqual(res.promoted, ["label:a"])           # b's perfect holdout cannot promote it
        self.assertEqual(res.n_test, 150)                      # scored on the holdout only
        self.assertEqual((res.auto_n, res.auto_errors), (100, 15))
        self.assertEqual(res.false_promotions, ["label:a"])    # 15% > 5% on the holdout
        self.assertAlmostEqual(res.coverage, 100 / 150)
        by = {r["category"]: r for r in rows}
        self.assertEqual(by["label:b"]["tier"], "review")
        self.assertEqual(by["label:b"]["hold_errors"], 0)

    def test_reliable_holdout_has_no_false_promotion(self):
        dev = recs("label:a", 400, 4)
        hold = recs("label:a", 100, 2, prefix="h")
        res, _ = run_holdout(dev, hold, CFG)
        self.assertEqual(res.promoted, ["label:a"])
        self.assertEqual(res.false_promotions, [])
        self.assertAlmostEqual(res.coverage, 1.0)

    def test_category_unseen_in_dev_is_never_auto(self):
        dev = recs("label:a", 400, 4)
        hold = recs("label:a", 50, 0, prefix="h") + recs("label:new", 50, 0, prefix="h")
        res, rows = run_holdout(dev, hold, CFG)
        self.assertEqual(res.promoted, ["label:a"])
        self.assertEqual(res.auto_n, 50)
        self.assertEqual({r["category"]: r["tier"] for r in rows}["label:new"], "review")

    def test_cli_prints_report(self):
        with tempfile.TemporaryDirectory() as d:
            dev, hold = os.path.join(d, "dev.jsonl"), os.path.join(d, "hold.jsonl")
            save_records(dev, recs("label:a", 400, 4))
            save_records(hold, recs("label:a", 100, 15, prefix="h"))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main([dev, hold])
        out = buf.getvalue()
        self.assertIn("false promotions: ['label:a']", out)
        self.assertIn("scored on 100 holdout records", out)


if __name__ == "__main__":
    unittest.main()
