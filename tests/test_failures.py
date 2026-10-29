import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import failures  # noqa: E402

ISSUES = [
    {"id": "a/b#1", "title": "Crash", "body": "x" * 500, "human_labels": ["bug"]},
    {"id": "a/b#2", "title": "Add thing", "body": "", "human_labels": ["feature", "docs"]},
    {"id": "a/b#3", "title": "How?", "body": "", "human_labels": ["question"]},
]
PREDS = [
    {"id": "a/b#1", "predicted": "feature", "human_labels": ["bug"]},        # wrong
    {"id": "a/b#2", "predicted": "docs", "human_labels": ["feature", "docs"]},   # right (multi-label)
    {"id": "a/b#3", "predicted": "bug", "human_labels": ["question"]},       # wrong
    {"id": "a/b#3", "predicted": "bug", "human_labels": ["question"]},       # duplicate row, counted once
]


class TestFailures(unittest.TestCase):
    def test_only_wrong_and_once(self):
        wrong = failures.wrong_predictions(ISSUES, PREDS)
        self.assertEqual([w["id"] for w in wrong], ["a/b#1", "a/b#3"])

    def test_render_has_url_and_short_excerpt(self):
        text = failures.render(failures.wrong_predictions(ISSUES, PREDS), total=3)
        self.assertIn("2 of 3", text)
        self.assertIn("https://github.com/a/b/issues/1", text)
        self.assertNotIn("x" * 400, text)          # body is cut to an excerpt
        self.assertIn("| feature | bug | 1 |", text)


if __name__ == "__main__":
    unittest.main()
