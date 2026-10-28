import json
import os
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

try:
    import duckdb  # noqa: F401
    HAVE_DUCKDB = True
except ImportError:
    HAVE_DUCKDB = False

from rung.backtest import temporal_backtest
from rung.policy import PolicyConfig
from rung.records import Record, load_records, save_records
from rung.stats import category_stats

if HAVE_DUCKDB:
    from rung import sqlstats

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)


def hours(i):
    return T0 + timedelta(hours=i)


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def py_backtest(path, max_error, min_n=30, frac=0.6):
    return temporal_backtest(load_records(path), PolicyConfig(max_error=max_error, min_n=min_n), frac)


@unittest.skipUnless(HAVE_DUCKDB, "pip install duckdb")
class TestStatsParity(unittest.TestCase):
    def test_matches_python_for_every_category(self):
        rng = random.Random(7)
        spec = {"label:bug": (500, 0.03), "label:docs": (120, 0.02), "label:small": (29, 0.1),
                "label:tiny": (3, 0.5), "label:clean": (40, 0.0)}
        recs, i = [], 0
        for cat, (n, err) in spec.items():
            for _ in range(n):
                recs.append(Record(f"id{i}", hours(i), cat, rng.random() >= err))
                i += 1
        rng.shuffle(recs)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            save_records(p, recs)
            sql = {r["category"]: r for r in sqlstats.category_stats_sql(p)}
        py = category_stats(recs)
        self.assertEqual(set(sql), set(py))
        for cat, s in py.items():
            self.assertEqual(sql[cat]["n"], s.n)
            self.assertEqual(sql[cat]["errors"], s.errors)
            self.assertAlmostEqual(sql[cat]["error_rate"], s.error_rate, delta=1e-9)
            self.assertAlmostEqual(sql[cat]["upper_bound"], s.upper_bound, delta=1e-9)
        self.assertEqual(sql["label:clean"]["errors"], 0)
        self.assertGreater(sql["label:clean"]["upper_bound"], 0)     # zero errors is still uncertain


@unittest.skipUnless(HAVE_DUCKDB, "pip install duckdb")
class TestBacktestParity(unittest.TestCase):
    def assert_same(self, path, max_error, frac=0.6, min_n=30):
        sql = sqlstats.temporal_backtest_sql(path, max_error=max_error, min_n=min_n, train_frac=frac)
        py = py_backtest(path, max_error, min_n, frac)
        self.assertEqual(sql["n_train"], py.n_train)
        self.assertEqual(sql["n_test"], py.n_test)
        self.assertEqual(sql["promoted"], py.promoted)
        self.assertEqual(sql["auto_n"], py.auto_n)
        self.assertEqual(sql["auto_errors"], py.auto_errors)
        self.assertEqual(sql["false_promotions"], py.false_promotions)
        self.assertAlmostEqual(sql["coverage"], py.coverage, delta=1e-12)
        self.assertAlmostEqual(sql["auto_error_rate"], py.auto_error_rate, delta=1e-12)
        return sql

    def test_unique_timestamps_shuffled_file(self):
        rng = random.Random(11)
        cats = {"label:a": 0.01, "label:b": 0.08, "label:c": 0.3}
        recs = [Record(f"i{i}", hours(i), c, rng.random() >= cats[c])
                for i in range(1500) for c in [rng.choice(list(cats))]]
        rng.shuffle(recs)                                   # file order != time order
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            save_records(p, recs)
            for me in (0.05, 0.15):
                self.assert_same(p, me)

    def test_heavily_tied_timestamps_use_file_order(self):
        # 21000 rows, only 6 distinct timestamps, and the 60% cut (row 12600) falls INSIDE a tie group.
        # Errors depend on file position, so any different tie-break changes the answer.
        rng = random.Random(5)
        recs = []
        for i in range(21000):
            cat = f"label:{'abc'[i % 3]}"
            err = 0.01 if i < 12000 else 0.30
            recs.append(Record(f"i{i}", hours(i // 3500), cat, rng.random() >= err))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            save_records(p, recs)
            for me in (0.05, 0.15):
                res = self.assert_same(p, me)
            self.assertTrue(res["promoted"])                 # the test is not vacuous
            self.assertTrue(res["false_promotions"])

    def test_float_edge_in_the_cut(self):
        # int(100 * 0.29) is 28 in Python (28.999999999999996); SQL must cut at the same row
        recs = [Record(f"i{i}", hours(i), "label:a", i % 10 != 0) for i in range(100)]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            save_records(p, recs)
            res = self.assert_same(p, 0.5, frac=0.29, min_n=5)
        self.assertEqual(res["n_train"], 28)

    def test_planted_degradation_is_a_false_promotion(self):
        rng = random.Random(3)
        recs = [Record(f"i{i}", hours(i), "label:docs", True if i < 300 else rng.random() >= 0.30)
                for i in range(500)]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            save_records(p, recs)
            res = self.assert_same(p, 0.05)
        self.assertEqual(res["promoted"], ["label:docs"])
        self.assertEqual(res["false_promotions"], ["label:docs"])

    def test_z_suffix_and_offset_timestamps(self):
        rng = random.Random(9)
        rows = []
        for i in range(200):
            instant = T0 + timedelta(minutes=i * 7)
            if i % 2:
                ts = instant.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                ts = (instant + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%dT%H:%M:%S+05:30")
            rows.append({"id": f"i{i}", "ts": ts, "category": "label:a" if i % 3 else "label:b",
                         "correct": rng.random() >= 0.02})
        rng.shuffle(rows)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            write_jsonl(p, rows)
            self.assert_same(p, 0.10, min_n=10)


@unittest.skipUnless(HAVE_DUCKDB, "pip install duckdb")
class TestCompare(unittest.TestCase):
    def test_intersection_only_first_duplicate_wins(self):
        rng = random.Random(1)
        a = [Record(f"i{i}", hours(i), f"label:{'xyz'[i % 3]}", rng.random() >= 0.1) for i in range(100)]
        b = [Record(f"i{i}", hours(i), f"label:{'xyz'[i % 3]}", rng.random() >= 0.3) for i in range(100)]
        b += [Record(f"i{i}", hours(i), "label:x", True) for i in range(100, 105)]       # 5 extra ids
        b += [Record("i5", hours(5), "label:z", not b[5].correct)]                         # repeated id
        with tempfile.TemporaryDirectory() as d:
            pa, pb = os.path.join(d, "a.jsonl"), os.path.join(d, "b.jsonl")
            save_records(pa, a)
            save_records(pb, b)
            res = sqlstats.compare_on_common_ids({"a": pa, "b": pb})
        self.assertEqual(res["counts"]["rows"], {"a": 100, "b": 106})
        self.assertEqual(res["counts"]["unique_ids"], {"a": 100, "b": 105})
        self.assertEqual(res["counts"]["common_ids"], 100)
        for name, recs in (("a", a), ("b", b)):
            first = {}
            for r in recs:
                first.setdefault(r.id, r)
            expected = category_stats([r for i, r in first.items() if i in {x.id for x in a}])
            got = {r["category"]: r for r in res["stats"][name]}
            self.assertEqual(set(got), set(expected))
            for cat, s in expected.items():
                self.assertEqual((got[cat]["n"], got[cat]["errors"]), (s.n, s.errors))
                self.assertAlmostEqual(got[cat]["upper_bound"], s.upper_bound, delta=1e-9)


@unittest.skipUnless(HAVE_DUCKDB, "pip install duckdb")
class TestQuality(unittest.TestCase):
    def test_counts(self):
        issues = [
            {"id": "r1#1", "repo": "r1", "created_at": "2026-01-01T00:00:00Z", "human_labels": ["bug"]},
            {"id": "r1#2", "repo": "r1", "created_at": "2026-01-03T00:00:00Z", "human_labels": ["docs", "feature"]},
            {"id": "r1#2", "repo": "r1", "created_at": "2026-01-03T00:00:00Z", "human_labels": ["docs", "feature"]},
            {"id": "r1#3", "repo": "r1", "human_labels": ["bug"]},                                  # no created_at
            {"id": "r2#1", "repo": "r2", "created_at": "2026-02-01T00:00:00Z", "human_labels": []},  # no labels
            {"id": "r2#2", "repo": "r2", "created_at": "2026-02-05T00:00:00Z", "human_labels": ["question"]},
        ]
        preds = [{"id": i} for i in ("r1#1", "r1#2", "r1#2", "r2#1", "r9#9")]
        with tempfile.TemporaryDirectory() as d:
            pi, pp = os.path.join(d, "i.jsonl"), os.path.join(d, "p.jsonl")
            write_jsonl(pi, issues)
            write_jsonl(pp, preds)
            rep = sqlstats.quality_report(pi, {"llm": pp})
        self.assertEqual(rep["rows"], 6)
        self.assertEqual(rep["unique_ids"], 5)
        self.assertEqual(rep["duplicate_ids"], 1)
        self.assertEqual(rep["extra_rows_from_duplicates"], 1)
        self.assertEqual(rep["missing_created_at"], 1)
        self.assertEqual(rep["missing_human_labels"], 1)
        self.assertEqual(rep["per_repo"]["r1"], {"rows": 4, "unique": 3, "first_created": "2026-01-01T00:00:00Z",
                                                 "last_created": "2026-01-03T00:00:00Z"})
        self.assertEqual(rep["per_repo"]["r2"], {"rows": 2, "unique": 2, "first_created": "2026-02-01T00:00:00Z",
                                                 "last_created": "2026-02-05T00:00:00Z"})
        self.assertEqual(rep["label_mix"], {"r1": {"bug": 2, "docs": 1, "feature": 1}, "r2": {"question": 1}})
        self.assertEqual(rep["predictions"]["llm"], {"rows": 5, "unique_ids": 4,
                                                     "issues_missing_from_preds": 2,
                                                     "pred_ids_not_in_issues": 1})


if __name__ == "__main__":
    unittest.main()
