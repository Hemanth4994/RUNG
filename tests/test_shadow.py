import json
import os
import tempfile
import unittest

from rung import baseline
from rung.gating import gate_tier, resolve_label
from rung.policy import AUTO, REVIEW
from rung.shadow import predictions_to_records, run_shadow

ISSUES = [
    {"id": "r#1", "created_at": "2026-01-01T00:00:00Z", "title": "App crashes on startup", "body": "", "human_labels": ["bug"]},
    {"id": "r#2", "created_at": "2026-01-02T00:00:00Z", "title": "How do I configure X?", "body": "", "human_labels": ["question"]},
    {"id": "r#3", "created_at": "2026-01-03T00:00:00Z", "title": "Fix typo in README", "body": "", "human_labels": ["docs"]},
    {"id": "r#4", "created_at": "2026-01-04T00:00:00Z", "title": "Add support for dark mode", "body": "", "human_labels": ["feature", "docs"]},
    {"id": "r#5", "created_at": "2026-01-05T00:00:00Z", "title": "Something odd", "body": "", "human_labels": ["question"]},
]


class TestBaseline(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(baseline.predict("App crashes on startup"), "bug")
        self.assertEqual(baseline.predict("How do I configure X?"), "question")
        self.assertEqual(baseline.predict("Fix typo in README"), "docs")
        self.assertEqual(baseline.predict("Add support for dark mode"), "feature")
        self.assertEqual(baseline.predict("Something odd"), "bug")  # documented default


class TestShadow(unittest.TestCase):
    def test_records_and_correctness(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            run_shadow(ISSUES, baseline.predict, out)
            recs = {r.id: r for r in predictions_to_records(out)}
        self.assertTrue(recs["r#1"].correct)
        self.assertEqual(recs["r#1"].category, "label:bug")
        self.assertTrue(recs["r#4"].correct)       # predicted feature, maintainers applied feature+docs
        self.assertFalse(recs["r#5"].correct)      # default 'bug' vs maintainers' 'question'

    def test_resumes_without_repeating_work(self):
        calls = []

        def counting(title, body):
            calls.append(title)
            return "bug"

        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            self.assertEqual(run_shadow(ISSUES, counting, out, limit=2), 2)
            self.assertEqual(run_shadow(ISSUES, counting, out), 3)   # only the remaining three
            self.assertEqual(run_shadow(ISSUES, counting, out), 0)   # nothing left
            with open(out) as f:
                ids = [json.loads(l)["id"] for l in f]
        self.assertEqual(len(calls), 5)
        self.assertEqual(len(set(ids)), 5)

    def test_invalid_prediction_counts_as_wrong(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "p.jsonl")
            run_shadow(ISSUES[:1], lambda t, b: "banana", out)
            rec = predictions_to_records(out)[0]
        self.assertEqual(rec.category, "label:invalid")
        self.assertFalse(rec.correct)


class TestGating(unittest.TestCase):
    POLICY = {"label:bug": AUTO, "label:question": REVIEW}

    def test_fail_closed(self):
        self.assertEqual(gate_tier("bug", self.POLICY), AUTO)
        self.assertEqual(gate_tier("question", self.POLICY), REVIEW)
        self.assertEqual(gate_tier("docs", self.POLICY), REVIEW)       # never seen -> human
        self.assertEqual(gate_tier("bug", {}), REVIEW)                 # empty policy -> human

    def test_resolve(self):
        self.assertEqual(resolve_label("bug", AUTO, None), "bug")
        self.assertEqual(resolve_label("question", REVIEW, "approve"), "question")
        self.assertEqual(resolve_label("question", REVIEW, "Docs"), "docs")
        self.assertIsNone(resolve_label("question", REVIEW, "reject"))
        self.assertIsNone(resolve_label("question", REVIEW, None))
        self.assertIsNone(resolve_label("question", REVIEW, "banana"))


if __name__ == "__main__":
    unittest.main()
