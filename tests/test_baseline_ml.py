import contextlib
import io
import json
import os
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

try:
    import sklearn  # noqa: F401
except ImportError:
    raise unittest.SkipTest("scikit-learn not installed: pip install scikit-learn")

from rung.baseline_ml import main, run, walk_forward_predictions
from rung.records import load_records
from rung.taxonomy import COARSE

PHRASES = {
    "bug": "crash traceback exception",
    "feature": "please add support feature request",
    "question": "how do I question usage",
    "docs": "typo documentation readme",
}
NOISE = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta"]
BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def stamp(i: int) -> str:
    return (BASE + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")


def synthetic(n: int = 200, seed: int = 1) -> list[dict]:
    """Issues with clearly separable vocabulary per label, in time order."""
    rng = random.Random(seed)
    issues = []
    for i in range(n):
        label = COARSE[rng.randrange(4)]
        words = " ".join(rng.choice(NOISE) for _ in range(3))
        issues.append({"id": f"r#{i}", "repo": "r", "created_at": stamp(i),
                       "title": f"{PHRASES[label]} {words}", "body": f"{words} {PHRASES[label]}",
                       "raw_labels": [label], "human_labels": [label]})
    return issues


def messy(n: int = 200) -> list[dict]:
    """synthetic() with 2-label and 0-label issues, shuffled input order and a duplicate id."""
    issues = synthetic(n)
    for i in range(0, n, 7):
        issues[i]["human_labels"] = ["bug", "docs"]
    for i in range(3, n, 11):
        issues[i]["human_labels"] = []
    issues.append(dict(issues[5], title="a later duplicate of r#5 with different text"))
    random.Random(2).shuffle(issues)
    return issues


class TestNoLeakage(unittest.TestCase):
    def test_trace_proves_no_leakage(self):
        issues = messy()
        trace: list = []
        walk_forward_predictions(issues, n_blocks=10, trace=trace)
        by_id = {}
        for d in issues:
            by_id.setdefault(d["id"], d)
        ts = {i: d["created_at"] for i, d in by_id.items()}
        order = sorted(by_id, key=lambda i: ts[i])           # unique ids, time order
        block0 = set(order[:len(order) // 10 + (1 if len(order) % 10 else 0)])
        self.assertTrue(any(t["mode"] == "cv" for t in trace))
        self.assertTrue(any(t["mode"] == "forward" for t in trace))
        for t in trace:
            train, pred = set(t["train_ids"]), set(t["predict_ids"])
            self.assertTrue(pred)
            self.assertEqual(train & pred, set())
            if t["mode"] == "cv":
                self.assertEqual(t["block"], 0)
                self.assertLessEqual(train | pred, block0)
            else:
                self.assertGreaterEqual(t["block"], 1)
                self.assertTrue(pred.isdisjoint(block0))
                if train:
                    self.assertLessEqual(max(ts[i] for i in train), min(ts[i] for i in pred))

    def test_every_unique_id_predicted_exactly_once_in_trace(self):
        issues = messy()
        trace: list = []
        walk_forward_predictions(issues, trace=trace)
        predicted = [i for t in trace for i in t["predict_ids"]]
        self.assertEqual(sorted(predicted), sorted({d["id"] for d in issues}))
        self.assertEqual(len(predicted), len(set(predicted)))

    def test_multi_label_and_unlabelled_issues_never_trained_on(self):
        issues = messy()
        untrainable = {d["id"] for d in issues if len(set(d["human_labels"])) != 1}
        self.assertTrue(any(len(d["human_labels"]) == 2 for d in issues))
        trace: list = []
        rows = walk_forward_predictions(issues, trace=trace)
        trained_on = {i for t in trace for i in t["train_ids"]}
        self.assertEqual(trained_on & untrainable, set())
        predicted_ids = {r["id"] for r in rows}
        self.assertTrue(untrainable <= predicted_ids)        # ...but they still get a prediction


class TestOutputShape(unittest.TestCase):
    def test_each_unique_id_once_in_time_order(self):
        issues = messy()
        rows = walk_forward_predictions(issues)
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {d["id"] for d in issues})
        self.assertEqual([r["created_at"] for r in rows], sorted(r["created_at"] for r in rows))
        for r in rows:
            self.assertEqual(set(r), {"id", "created_at", "predicted", "human_labels"})

    def test_first_duplicate_wins(self):
        issues = [{"id": "r#1", "created_at": stamp(1), "title": "crash", "body": "", "human_labels": ["bug"]},
                  {"id": "r#1", "created_at": stamp(2), "title": "other", "body": "", "human_labels": ["docs"]}]
        rows = walk_forward_predictions(issues)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["created_at"], stamp(1))
        self.assertEqual(rows[0]["human_labels"], ["bug"])

    def test_predictions_in_coarse(self):
        for issues in (messy(), synthetic(30)):
            for r in walk_forward_predictions(issues):
                self.assertIn(r["predicted"], COARSE)

    def test_tiny_inputs_do_not_crash(self):
        self.assertEqual(walk_forward_predictions([]), [])
        one = synthetic(1)
        three = [{"id": f"r#{i}", "created_at": stamp(i), "title": f"{w} unique{i}", "body": "",
                  "human_labels": [lab]} for i, (w, lab) in
                 enumerate([("crash", "bug"), ("add feature", "feature"), ("how do i", "question")])]
        for issues in (one, synthetic(2), three, synthetic(3), synthetic(7)):
            for kw in ({}, {"n_blocks": 1}, {"n_blocks": 50}, {"n_folds": 1}):
                rows = walk_forward_predictions(issues, **kw)
                self.assertEqual(len(rows), len(issues))
                self.assertTrue(all(r["predicted"] in COARSE for r in rows))

    def test_single_issue_falls_back_to_bug(self):
        rows = walk_forward_predictions([{"id": "r#1", "created_at": stamp(0), "title": "t",
                                          "body": "", "human_labels": ["docs"]}])
        self.assertEqual(rows[0]["predicted"], "bug")

    def test_empty_or_missing_text_does_not_crash(self):
        issues = [{"id": f"r#{i}", "created_at": stamp(i), "title": None, "body": None,
                   "human_labels": [COARSE[i % 4]]} for i in range(12)]
        issues.append({"id": "r#x", "created_at": stamp(99), "title": "x"})   # no body, no labels
        rows = walk_forward_predictions(issues, n_blocks=3)
        self.assertEqual(len(rows), 13)

    def test_deterministic(self):
        issues = messy()
        self.assertEqual(walk_forward_predictions(issues), walk_forward_predictions(issues))
        t1: list = []
        t2: list = []
        walk_forward_predictions(issues, trace=t1)
        walk_forward_predictions(issues, trace=t2)
        self.assertEqual(t1, t2)


class TestLearns(unittest.TestCase):
    def test_accuracy_on_later_blocks(self):
        issues = synthetic(200)
        rows = walk_forward_predictions(issues, n_blocks=10)
        later = rows[20:]                                    # everything after block 0
        self.assertEqual(len(later), 180)
        acc = sum(r["predicted"] in r["human_labels"] for r in later) / len(later)
        self.assertGreater(acc, 0.8)


class TestRun(unittest.TestCase):
    def _write(self, d: str, issues: list[dict]) -> str:
        path = os.path.join(d, "issues.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for issue in issues:
                f.write(json.dumps(issue) + "\n")
        return path

    def test_run_writes_predictions_and_loadable_records(self):
        issues = messy(60)
        with tempfile.TemporaryDirectory() as d:
            src = self._write(d, issues)
            out, rec = os.path.join(d, "sub", "p.jsonl"), os.path.join(d, "sub2", "r.jsonl")
            n = run(src, out, rec, n_blocks=5)
            self.assertTrue(os.path.exists(out))
            self.assertTrue(os.path.exists(rec))
            records = load_records(rec)
            n_unique = len({x["id"] for x in issues})
            self.assertEqual((n, len(records)), (n_unique, n_unique))
            self.assertTrue(all(r.category.startswith("label:") for r in records))
            with open(out, encoding="utf-8") as f:
                first = f.read()
            run(src, out, rec, n_blocks=5)                   # overwrite, not append
            with open(out, encoding="utf-8") as f:
                self.assertEqual(f.read(), first)
            self.assertEqual(len(load_records(rec)), n_unique)

    def test_main_prints_summary(self):
        with tempfile.TemporaryDirectory() as d:
            src = self._write(d, synthetic(40))
            out, rec = os.path.join(d, "p.jsonl"), os.path.join(d, "r.jsonl")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main([src, "--out", out, "--records", rec, "--blocks", "4"])
            self.assertTrue(buf.getvalue().startswith("40 predictions -> "))
            self.assertEqual(len(load_records(rec)), 40)


if __name__ == "__main__":
    unittest.main()
