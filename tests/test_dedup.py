import importlib.util
import json
import os
import tempfile
import unittest

from rung.collect import existing_ids
from rung.shadow import predictions_to_records, run_shadow

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("check_data", os.path.join(ROOT, "scripts", "check_data.py"))
check_data = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_data)


def issue(n, created="2026-01-01T00:00:00Z", repo="r"):
    return {"id": f"{repo}#{n}", "created_at": created, "title": "App crashes", "body": "",
            "human_labels": ["bug"]}


class TestShadowDedup(unittest.TestCase):
    def test_repeated_id_in_input_is_predicted_once(self):
        calls = []

        def counting(title, body):
            calls.append(title)
            return "bug"

        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            n = run_shadow([issue(1), issue(2), issue(1)], counting, out)
            with open(out) as f:
                written = [json.loads(line)["id"] for line in f]
        self.assertEqual(n, 2)
        self.assertEqual(len(calls), 2)
        self.assertEqual(sorted(written), ["r#1", "r#2"])

    def test_duplicate_prediction_rows_count_once_in_records(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            row = {"id": "r#1", "created_at": "2026-01-01T00:00:00Z", "predicted": "bug",
                   "human_labels": ["bug"]}
            with open(out, "w") as f:
                for _ in range(3):
                    f.write(json.dumps(row) + "\n")
            recs = predictions_to_records(out)
        self.assertEqual(len(recs), 1)


class TestCollectHelper(unittest.TestCase):
    def test_existing_ids(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "i.jsonl")
            self.assertEqual(existing_ids(p), set())          # missing file -> empty set
            with open(p, "w") as f:
                f.write(json.dumps(issue(1)) + "\n" + json.dumps(issue(2)) + "\n")
            self.assertEqual(existing_ids(p), {"r#1", "r#2"})


class TestCheckData(unittest.TestCase):
    def test_issue_report_counts_duplicates(self):
        rep = check_data.check_issues([issue(1), issue(1), issue(2, repo="s")])
        self.assertEqual(rep["rows"], 3)
        self.assertEqual(rep["unique_ids"], 2)
        self.assertEqual(rep["extra_rows_from_duplicates"], 1)
        self.assertEqual(rep["per_repo"], {"r": 2, "s": 1})

    def test_compare_finds_the_extra_rows_and_their_dates(self):
        a = [{"id": f"r#{i}", "created_at": "2026-01-01T00:00:00Z"} for i in range(1, 4)]
        b = a + [{"id": "r#4", "created_at": "2026-02-01T00:00:00Z"},
                 {"id": "r#5", "created_at": "2026-02-03T00:00:00Z"}]
        rep = check_data.compare_predictions(a, b)
        self.assertEqual(rep["only_in_a"], [])
        self.assertEqual(rep["only_in_b"], ["r#4", "r#5"])
        self.assertEqual(rep["only_in_b_created_between"],
                         ("2026-02-01T00:00:00Z", "2026-02-03T00:00:00Z"))


if __name__ == "__main__":
    unittest.main()
