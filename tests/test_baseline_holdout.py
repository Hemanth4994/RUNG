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

from rung.baseline_ml import main, predict_with_training_set, run
from rung.records import load_records
from rung.taxonomy import COARSE

PHRASES = {"bug": "crash traceback exception", "feature": "please add support feature request",
           "question": "how do I question usage", "docs": "typo documentation readme"}
BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def issues(n, prefix, seed, offset=0):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        label = rng.choice(list(PHRASES))
        out.append({"id": f"{prefix}#{i}", "created_at": (BASE + timedelta(hours=offset + i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "title": f"{PHRASES[label]} {rng.choice(['alpha', 'beta', 'gamma'])}", "body": "",
                    "human_labels": [label]})
    return out


class TestHoldoutMode(unittest.TestCase):
    def test_learns_from_dev_and_predicts_unseen_repo(self):
        dev, hold = issues(300, "dev", 1), issues(120, "hold", 2, offset=50)
        rows = predict_with_training_set(dev, hold)
        self.assertEqual(len(rows), 120)
        acc = sum(r["predicted"] in r["human_labels"] for r in rows) / len(rows)
        self.assertGreater(acc, 0.8)
        self.assertTrue(all(r["predicted"] in COARSE for r in rows))

    def test_test_ids_are_never_trained_on_and_duplicates_dropped(self):
        dev = issues(100, "dev", 1)
        hold = issues(20, "hold", 2)
        overlap = dict(dev[0]); overlap["human_labels"] = ["docs"]       # same id as a test issue
        hold_with_overlap = hold + [dict(dev[0]), dict(hold[0])]          # + a repeated id
        trace = []
        rows = predict_with_training_set(dev + [overlap], hold_with_overlap, trace=trace)
        t = trace[0]
        self.assertEqual(set(t["train_ids"]) & set(t["predict_ids"]), set())
        self.assertNotIn(dev[0]["id"], t["train_ids"])
        ids = [r["id"] for r in rows]
        self.assertEqual(len(ids), len(set(ids)))                         # each test id once
        self.assertEqual(len(ids), 21)

    def test_multi_label_dev_issues_are_not_training_rows(self):
        dev = issues(50, "dev", 1)
        dev[0]["human_labels"] = ["bug", "docs"]
        trace = []
        predict_with_training_set(dev, issues(5, "hold", 2), trace=trace)
        self.assertNotIn(dev[0]["id"], trace[0]["train_ids"])

    def test_empty_inputs(self):
        self.assertEqual(predict_with_training_set([], []), [])
        rows = predict_with_training_set([], issues(3, "hold", 2))
        self.assertEqual([r["predicted"] for r in rows], ["bug"] * 3)     # documented fallback

    def test_cli_train_on_writes_loadable_records(self):
        with tempfile.TemporaryDirectory() as d:
            dev, hold = os.path.join(d, "dev.jsonl"), os.path.join(d, "hold.jsonl")
            for path, rows in ((dev, issues(200, "dev", 1)), (hold, issues(60, "hold", 2, offset=10))):
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(json.dumps(r) + "\n" for r in rows)
            out, rec = os.path.join(d, "p.jsonl"), os.path.join(d, "r.jsonl")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main([hold, "--train-on", dev, "--out", out, "--records", rec])
            records = load_records(rec)
        self.assertEqual(len(records), 60)
        self.assertIn("60 predictions", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
