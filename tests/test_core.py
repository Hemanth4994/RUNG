import unittest
from datetime import datetime, timedelta, timezone

from rung.backtest import temporal_backtest
from rung.policy import AUTO, REVIEW, PolicyConfig, build_policy
from rung.records import Record
from rung.stats import category_stats, wilson_upper
from rung.taxonomy import coarse_labels

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def recs(category, n, n_errors, start=0):
    return [Record(f"{category}{start+i}", T0 + timedelta(hours=start + i), category, i >= n_errors)
            for i in range(n)]


class TestStats(unittest.TestCase):
    def test_no_data_means_no_trust(self):
        self.assertEqual(wilson_upper(0, 0), 1.0)

    def test_known_value(self):
        self.assertAlmostEqual(wilson_upper(0, 100), 0.0263, delta=0.001)

    def test_more_data_tightens_bound(self):
        self.assertGreater(wilson_upper(0, 10), wilson_upper(0, 100))

    def test_bound_above_point_estimate(self):
        s = category_stats(recs("a", 100, 5))["a"]
        self.assertAlmostEqual(s.error_rate, 0.05)
        self.assertGreater(s.upper_bound, s.error_rate)


class TestPolicy(unittest.TestCase):
    def test_small_sample_is_not_promoted(self):
        # 0 errors in 10 looks perfect but is not enough evidence
        p = build_policy(recs("a", 10, 0), PolicyConfig(max_error=0.05, min_n=30))
        self.assertEqual(p["a"], REVIEW)

    def test_reliable_large_sample_is_promoted(self):
        p = build_policy(recs("a", 300, 3), PolicyConfig(max_error=0.05, min_n=30))
        self.assertEqual(p["a"], AUTO)

    def test_high_error_is_not_promoted(self):
        p = build_policy(recs("a", 300, 60), PolicyConfig(max_error=0.05, min_n=30))
        self.assertEqual(p["a"], REVIEW)


class TestBacktest(unittest.TestCase):
    def test_catches_degradation_after_promotion(self):
        # category is perfect in the past, bad in the future -> must show up as a false promotion
        past = recs("docs", 300, 0, start=0)
        future = recs("docs", 200, 60, start=300)
        res = temporal_backtest(past + future, PolicyConfig(max_error=0.05, min_n=30), train_frac=0.6)
        self.assertEqual(res.promoted, ["docs"])
        self.assertEqual(res.false_promotions, ["docs"])
        self.assertGreater(res.auto_error_rate, 0.05)

    def test_stable_category_has_no_false_promotion(self):
        data = recs("bug", 500, 5)
        res = temporal_backtest(data, PolicyConfig(max_error=0.05, min_n=30))
        self.assertEqual(res.false_promotions, [])
        self.assertGreater(res.coverage, 0.9)


class TestTaxonomy(unittest.TestCase):
    def test_mapping(self):
        self.assertEqual(coarse_labels(["type: bug", "help wanted"]), {"bug"})
        self.assertEqual(coarse_labels(["Documentation", "enhancement"]), {"docs", "feature"})
        self.assertEqual(coarse_labels(["good first issue"]), set())


if __name__ == "__main__":
    unittest.main()
